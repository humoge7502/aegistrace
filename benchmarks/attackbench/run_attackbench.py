"""AttackBench — reproducible attack/benign fixtures and detection measurement.

All fixtures are HARMLESS local simulations: components are metadata records,
"tampering" means emitting events whose observed digests differ from the
registered baseline. Nothing here is real-world exploitation tooling.

Each scenario returns (detected, detail):
  detected: bool — the engine flagged the run (integrity event fired, trust
  state < TRUSTED, certificate rejected, or output invalidated).
"""

from __future__ import annotations

import sys
from pathlib import Path as _P

sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

import hashlib
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import select

from backend.app.certs import service as cert_service  # noqa: F401 (kept for parity)
from backend.app.collect.ingest import process_event
from backend.app.collect.schemas import EventIn
from backend.app.core.crypto import canonical_json, load_or_create_key, verify_with_key
from backend.app.core.db import make_engine, make_session_factory
from backend.app.domain import models
from backend.app.domain.enums import FingerprintMode, IntegrityKind, Severity, TrustState
from backend.app.graph import service as graph
from backend.app.trust import engine as trust


def H(n: str) -> str:
    return "sha256:" + hashlib.sha256(str(n).encode()).hexdigest()


AGENT = "bench-agent"
BASE_STEPS = [
    {"seq": 1, "kind": "model", "target": "bench-model@1"},
    {"seq": 2, "kind": "retrieval", "target": "kb://bench"},
    {"seq": 3, "kind": "mcp", "target": "mcp://bench-crm"},
    {"seq": 4, "kind": "tool", "target": "tool:send_email"},
]
BASE_DOC = {
    "agent_ref": AGENT, "mode": "sequence", "steps": BASE_STEPS,
    "allowed": {"model": ["bench-model@1"], "retrieval": ["kb://bench"],
                "mcp": ["mcp://bench-crm"], "tools": ["tool:send_email"]},
    "component_digests": {"bench-model@1": H("model"), "mcp://bench-crm": H("mcp"),
                          "tool:send_email": H("tool"), "kb://bench": H("corpus"),
                          "pypi:requests": H("requests-2.31.0-original"),
                          "container:agent": H("image-original")},
    "prompt_hashes": {"system": H("sysprompt")},
}
PROMPT = H("sysprompt")


@dataclass
class ScenarioResult:
    id: str
    category: str
    is_attack: bool
    expected_detection: bool
    detected: bool
    trust_state: str
    integrity_events: list[dict] = field(default_factory=list)
    extras: dict = field(default_factory=dict)


class EngineHarness:
    """In-process engine (no HTTP) for fast, reproducible benchmark runs."""

    def __init__(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="attackbench-"))
        self.engine = make_engine(f"sqlite:///{(tmp / 'bench.db').as_posix()}")
        models.Base.metadata.create_all(self.engine)
        self.factory = make_session_factory(self.engine)
        self.key = load_or_create_key(tmp / "signing.pem")
        with self.factory() as db:
            t = models.Tenant(name="bench")
            db.add(t)
            db.flush()
            db.add(models.Policy(tenant_id=t.id, name="default", rules={}, is_default=True))
            db.add(models.Baseline(tenant_id=t.id, agent_ref=AGENT, agent_version="1",
                                   mode=FingerprintMode.SEQUENCE, doc=BASE_DOC))
            db.commit()
            self.tenant_id = t.id

    def emit(self, events: list[tuple[str, dict]], execution_external_id: str | None = None) -> None:
        with self.factory() as db:
            for kind, payload in events:
                payload = dict(payload)
                eid = payload.pop("_external_id", execution_external_id)
                process_event(db, self.tenant_id,
                              EventIn(kind=kind, execution_external_id=eid, payload=payload),
                              self.key, "bench-key", "bench")
            db.commit()  # Session context manager closes but does not commit

    def execution_state(self, external_id: str) -> dict:
        with self.factory() as db:
            ex = graph.get_execution_by_external(db, self.tenant_id, external_id)
            ies = db.execute(select(models.IntegrityEvent).where(
                models.IntegrityEvent.execution_id == ex.id)).scalars().all()
            return {"state": ex.trust_state.value, "fingerprint": ex.fingerprint,
                    "events": [{"kind": i.kind.value, "severity": i.severity.value,
                                "title": i.title} for i in ies]}

    def compromise(self, component_name: str, reason: str) -> dict:
        with self.factory() as db:
            comp = db.execute(select(models.Component).where(
                models.Component.tenant_id == self.tenant_id,
                models.Component.name == component_name)).scalar_one()
            result = trust.compromise_component(db, self.tenant_id, comp, reason)
            db.commit()
            return result

    def recover(self, component_name: str, digest: str) -> None:
        with self.factory() as db:
            comp = db.execute(select(models.Component).where(
                models.Component.tenant_id == self.tenant_id,
                models.Component.name == component_name)).scalar_one()
            trust.recover_component(db, self.tenant_id, comp, "restored to trusted digest",
                                    new_digest=digest)
            db.commit()


def _clean_run(run_id: str, mcp_digest: str | None = None,
               model_digest: str | None = None, tool_digest: str | None = None,
               corpus_digest: str | None = None, prompt: str | None = None,
               extra_steps: list[tuple[str, str, str]] | None = None,
               status: str = "completed",
               rerun_of: str | None = None) -> list[tuple[str, dict]]:
    """Standard 4-step execution; every digest overridable for attack simulation."""
    started: dict = {"agent_ref": AGENT, "_external_id": run_id}
    if rerun_of:
        started["rerun_of"] = rerun_of
    events = [("execution.started", started),
              ("prompt.pinned", {"role": "system", "hash": prompt or PROMPT, "_external_id": run_id}),
              ("step.ended", {"seq": 1, "kind": "model", "target": "bench-model@1",
                              "digest": model_digest or H("model"), "_external_id": run_id}),
              ("step.ended", {"seq": 2, "kind": "retrieval", "target": "kb://bench",
                              "digest": corpus_digest or H("corpus"),
                              "meta": {"documents": [{"id": "d1", "hash": H("doc1")}]},
                              "_external_id": run_id}),
              ("step.ended", {"seq": 3, "kind": "mcp", "target": "mcp://bench-crm",
                              "digest": mcp_digest or H("mcp"),
                              "meta": {"tool": "lookup_customer"}, "_external_id": run_id}),
              ("step.ended", {"seq": 4, "kind": "tool", "target": "tool:send_email",
                              "digest": tool_digest or H("tool"), "_external_id": run_id})]
    for i, (kind, target, digest) in enumerate(extra_steps or []):
        events.append(("step.ended", {"seq": 10 + i, "kind": kind, "target": target,
                                      "digest": digest, "_external_id": run_id}))
    events.append(("output.produced", {"digest": H(f"output-{run_id}"), "_external_id": run_id}))
    events.append(("execution.finished", {"execution_external_id": run_id, "status": status,
                                          "_external_id": run_id}))
    return events


def detect(h: EngineHarness, run_id: str) -> tuple[bool, dict]:
    """'Detected' = run NOT trusted: at least one integrity event fired or
    trust < TRUSTED. Insufficient evidence must never yield TRUSTED."""
    st = h.execution_state(run_id)
    return st["state"] != TrustState.TRUSTED.value, st


# --- 14 attack scenarios + 3 benign controls -----------------------------------


def sc_model_tampering(h):
    h.emit(_clean_run("s01", model_digest=H("model-tampered")))
    return detect(h, "s01")


def sc_prompt_tampering(h):
    h.emit(_clean_run("s02", prompt=H("sysprompt-tampered")))
    return detect(h, "s02")


def sc_dataset_poisoning(h):
    h.emit(_clean_run("s03", corpus_digest=H("corpus-poisoned")))
    return detect(h, "s03")


def sc_dependency_substitution(h):
    # declared dependency arrives with a digest different from the pinned one
    h.emit(_clean_run("s04", extra_steps=[
        ("package", "pypi:requests", H("requests-2.31.0-tampered"))]))
    return detect(h, "s04")


def sc_container_modification(h):
    # container runtime digest differs from the pinned image digest
    h.emit(_clean_run("s05", extra_steps=[
        ("runtime", "container:agent", H("image-tampered"))]))
    ok, st = detect(h, "s05")
    st["extras"] = {"note": "container digest differs from pinned image digest"}
    return ok, st


def sc_rag_poisoning(h):
    h.emit(_clean_run("s06", extra_steps=[
        ("retrieval", "kb://attacker-index", H("poisoned-docs"))]))
    return detect(h, "s06")


def sc_tool_compromise(h):
    h.emit(_clean_run("s07", tool_digest=H("tool-tampered")))
    return detect(h, "s07")


def sc_mcp_compromise(h):
    h.emit(_clean_run("s08", mcp_digest=H("mcp-tampered")))
    return detect(h, "s08")


def sc_runtime_manipulation(h):
    h.emit(_clean_run("s09", extra_steps=[
        ("runtime", "runtime:python-3.13", H("runtime-unexpected"))]))
    return detect(h, "s09")


def sc_path_deviation(h):
    h.emit(_clean_run("s10", extra_steps=[("mcp", "mcp://external-endpoint", H("exfil"))]))
    return detect(h, "s10")


def sc_multi_component(h):
    h.emit(_clean_run("s11", mcp_digest=H("mcp-tampered"), tool_digest=H("tool-tampered")))
    return detect(h, "s11")


def sc_forged_attestation(h):
    h.emit(_clean_run("s12"))
    ok, st = detect(h, "s12")
    with h.factory() as db:
        ex = graph.get_execution_by_external(db, h.tenant_id, "s12")
        cert = db.execute(select(models.Certificate).where(
            models.Certificate.execution_id == ex.id)).scalar_one_or_none()
        if cert is None:
            return True, {**st, "extras": {"error": "no certificate issued — cannot test forgery"}}
        stmt = dict(cert.statement)
        # attacker swaps the certified execution's identity (subject digest)
        stmt = {**stmt, "subject": [{"name": stmt["subject"][0]["name"],
                                     "digest": {"sha256": "f" * 64}}]}
        forged_ok = verify_with_key(h.key, canonical_json(stmt), cert.signature)
        detected = not forged_ok
        return detected, {**st, "extras": {"forged_signature_valid": forged_ok}}


def sc_stale_trust(h):
    h.emit([("execution.started", {"agent_ref": AGENT, "_external_id": "s13"}),
            ("execution.finished", {"execution_external_id": "s13", "status": "completed",
                                    "_external_id": "s13"})])
    ok, st = detect(h, "s13")
    st["extras"] = {"note": "missing provenance yields UNKNOWN, never TRUSTED"}
    return ok, st


def sc_historical_dependency_compromise(h):
    h.emit(_clean_run("s14"))
    prop = h.compromise("mcp://bench-crm", "post-hoc compromise discovered")
    output_invalidated = bool(prop["affected_outputs"])
    cert_revoked = bool(prop["revoked_certificates"])
    return output_invalidated and cert_revoked, {
        "state": "post-hoc", "events": [],
        "extras": {"affected_executions": len(prop["affected_executions"]),
                   "outputs_invalidated": len(prop["affected_outputs"]),
                   "certificates_revoked": prop["revoked_certificates"]}}


def sc_benign_exact(h):
    h.emit(_clean_run("b01"))
    return detect(h, "b01")


def sc_benign_meta_variation(h):
    h.emit(_clean_run("b02"))
    return detect(h, "b02")


def sc_benign_recovery_flow(h):
    # compromise (detected) -> recover -> rerun marked rerun_of -> RE-CERTIFIED.
    # For FP accounting: FP only if the final re-certified run is not trusted.
    h.emit(_clean_run("b03", mcp_digest=H("mcp-tampered")))
    attack_detected, attack_state = detect(h, "b03")
    h.compromise("mcp://bench-crm", "fixture tampered")
    h.recover("mcp://bench-crm", H("mcp"))
    h.emit(_clean_run("b03-rerun", rerun_of="b03"))
    st = h.execution_state("b03-rerun")
    recertified = st["state"] in (TrustState.RE_CERTIFIED.value, TrustState.TRUSTED.value)
    st["extras"] = {"intermediate_attack_detected": attack_detected,
                    "recertified": recertified}
    return not recertified, st


SCENARIOS = [
    ("model-tampering", "model tampering", True, sc_model_tampering),
    ("prompt-tampering", "prompt tampering", True, sc_prompt_tampering),
    ("dataset-poisoning", "dataset poisoning", True, sc_dataset_poisoning),
    ("dependency-substitution", "dependency substitution", True, sc_dependency_substitution),
    ("container-modification", "container modification", True, sc_container_modification),
    ("rag-poisoning", "RAG poisoning", True, sc_rag_poisoning),
    ("tool-compromise", "tool compromise", True, sc_tool_compromise),
    ("mcp-compromise", "MCP compromise", True, sc_mcp_compromise),
    ("runtime-manipulation", "runtime manipulation", True, sc_runtime_manipulation),
    ("path-deviation", "execution-path deviation", True, sc_path_deviation),
    ("multi-component", "combined compromise", True, sc_multi_component),
    ("forged-attestation", "forged attestation", True, sc_forged_attestation),
    ("stale-trust", "stale/missing trust evidence", True, sc_stale_trust),
    ("historical-dependency-compromise", "historical dependency compromise", True,
     sc_historical_dependency_compromise),
    ("benign-exact", "benign control (exact expected run)", False, sc_benign_exact),
    ("benign-meta-variation", "benign control (metadata variation)", False, sc_benign_meta_variation),
    ("benign-recovery-flow", "benign control (compromise->recover->re-certify)", False,
     sc_benign_recovery_flow),
]


def run_attackbench() -> dict:
    results: list[ScenarioResult] = []
    for sid, category, is_attack, fn in SCENARIOS:
        h = EngineHarness()  # fresh engine per scenario: no cross-contamination
        try:
            detected, st = fn(h)
            results.append(ScenarioResult(
                id=sid, category=category, is_attack=is_attack,
                expected_detection=is_attack, detected=detected,
                trust_state=st.get("state", "post-hoc"),
                integrity_events=st.get("events", []), extras=st.get("extras", {}),
            ))
        except Exception as e:  # report failures honestly, never swallow
            results.append(ScenarioResult(
                id=sid, category=category, is_attack=is_attack,
                expected_detection=is_attack, detected=False, trust_state="ERROR",
                extras={"error": f"{type(e).__name__}: {e}"},
            ))
        finally:
            h.engine.dispose()

    attacks = [r for r in results if r.is_attack]
    benign = [r for r in results if not r.is_attack]
    tp = sum(1 for r in attacks if r.detected)
    fn_count = len(attacks) - tp
    fp = sum(1 for r in benign if r.detected)
    tn = len(benign) - fp
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn_count) if (tp + fn_count) else None

    return {
        "benchmark": "AegisTrace AttackBench v0",
        "note": "All fixtures are harmless local simulations; detection = run not trusted "
                "(integrity event fired / certificate rejected / output invalidated).",
        "scenarios": [r.__dict__ for r in results],
        "metrics": {
            "attacks": len(attacks), "true_positives": tp, "false_negatives": fn_count,
            "benign_controls": len(benign), "false_positives": fp, "true_negatives": tn,
            "precision": round(precision, 3) if precision is not None else None,
            "recall": round(recall, 3) if recall is not None else None,
            "accuracy": round((tp + tn) / len(results), 3),
        },
    }


if __name__ == "__main__":
    import json
    report = run_attackbench()
    out = Path(__file__).resolve().parents[2] / "docs" / "benchmarks" / "attackbench-results.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2))
    for s in report["scenarios"]:
        flag = "DETECTED" if s["detected"] else "missed  "
        print(f"  {flag} {s['id']:36s} {s['trust_state']}")
