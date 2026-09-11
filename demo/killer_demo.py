"""AegisTrace — Killer Demo (the definitive technical experiment).

Reproducible end-to-end demonstration against a REAL server over HTTP with the
REAL SDK. Everything is local and harmless: the "model" is a simulated fixture,
the "MCP server" and "CRM" are local stand-ins. All data produced here is
DEMO DATA.

Scenario:
  Phase 1  Normal execution            -> TRUSTED + AI Trust Certificate
  Phase 2  MCP fixture tampered        -> digest mismatch -> UNTRUSTED
  Phase 3  Execution path deviation    -> output looks normal -> UNTRUSTED
  Phase 4  Historical impact analysis  -> previous output invalidated, cert revoked
  Phase 5  Recovery + re-run           -> RE-CERTIFIED

Run:  python demo/killer_demo.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import httpx
import uvicorn

HOST, PORT = "127.0.0.1", 8420
BASE = f"http://{HOST}:{PORT}"

# --- local fixture digests (harmless simulation) ---
D_MODEL = "sha256:" + "aa" * 32          # demo-model@1
D_MCP_TRUSTED = "sha256:" + "bb" * 32    # mcp://crm-fixture (trusted build)
D_MCP_TAMPERED = "sha256:" + "cc" * 32   # same path, tampered payload
D_TOOL = "sha256:" + "dd" * 32           # tool:send_email
SYSTEM_PROMPT = "You are the support agent. Answer from the policy KB."
DEMO_DIGESTS = {"demo-model@1": D_MODEL, "mcp://crm-fixture": D_MCP_TRUSTED, "tool:send_email": D_TOOL}


def banner(text: str) -> None:
    print(f"\n{'=' * 72}\n  {text}\n{'=' * 72}")


def wait_ready(client: httpx.Client) -> None:
    for _ in range(80):
        try:
            if client.get(f"{BASE}/healthz").status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("server did not become ready")


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="aegistrace-demo-")
    os.environ["AEGISTRACE_DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/demo.db"
    os.environ["AEGISTRACE_SIGNING_KEY_PATH"] = f"{tmp.replace(chr(92), '/')}/signing.pem"
    os.environ["AEGISTRACE_BOOTSTRAP_KEY"] = "at_demo_bootstrap_key_do_not_use_in_prod"
    from backend.app.core.config import get_settings
    get_settings.cache_clear()

    from backend.app.main import create_app
    app = create_app()
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()

    admin_key = "at_demo_bootstrap_key_do_not_use_in_prod"
    with httpx.Client(timeout=10) as c:
        wait_ready(c)
        agent_key = c.post(f"{BASE}/api/v1/auth/keys", headers={"X-API-Key": admin_key},
                           json={"name": "demo-agent", "role": "agent"}).json()["key"]

        # --- baseline: the EXPECTED execution contract -----------------------
        r = c.post(f"{BASE}/api/v1/baselines", headers={"X-API-Key": admin_key}, json={
            "agent_ref": "support-agent", "agent_version": "1.0.0", "mode": "sequence",
            "steps": [
                {"seq": 1, "kind": "model", "target": "demo-model@1"},
                {"seq": 2, "kind": "retrieval", "target": "kb://policies"},
                {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture"},
                {"seq": 4, "kind": "tool", "target": "tool:send_email"},
            ],
            "allowed": {"model": ["demo-model@1"], "retrieval": ["kb://policies"],
                        "mcp": ["mcp://crm-fixture"], "tools": ["tool:send_email"]},
            "component_digests": DEMO_DIGESTS,
            "prompt_hashes": {"system": _hash(SYSTEM_PROMPT)},
        })
        assert r.status_code == 200, r.text
        print(f"baseline registered for support-agent@1.0.0 (mode=sequence)")

        # --- instrument the SDK against the real server ----------------------
        import aegistrace
        from aegistrace.integrations import mcp as at_mcp
        from aegistrace.integrations import rag as at_rag
        from aegistrace.integrations import tools as at_tools

        aegistrace.init(endpoint=BASE, api_key=agent_key,
                        agent_ref="support-agent", agent_version="1.0.0")

        @at_tools.tool("tool:send_email")
        def send_email(to: str, body: str) -> str:
            return f"email sent to {to}"

        def run_support_agent(question: str, mcp_digest: str, run_id: str | None = None,
                              inject_unexpected_call: bool = False,
                              rerun_of: str | None = None) -> str:
            """DEMO agent: simulated model + retrieval + MCP CRM call + email tool."""
            ctx = aegistrace.start_run(run_id=run_id, rerun_of=rerun_of)
            try:
                aegistrace.pin_prompt("system", SYSTEM_PROMPT)
                with aegistrace.step("model", "demo-model@1", digest=D_MODEL):
                    answer_draft = f"Simulated model reasoning about: {question}"
                with aegistrace.step("retrieval", "kb://policies") as s:
                    docs = [{"id": "pol-001", "text": "Refund window is 30 days."},
                            {"id": "pol-002", "text": "Escalate billing disputes to tier-2."}]
                    s.record_documents(docs)
                with aegistrace.step("mcp", "mcp://crm-fixture", digest=mcp_digest,
                                     meta={"tool": "lookup_customer"}) as s:
                    crm_record = {"customer": "C-123", "tier": "gold"}  # simulated CRM response
                    if inject_unexpected_call:
                        with aegistrace.step("mcp", "mcp://external-attacker-fixture",
                                             digest="sha256:" + "ef" * 32):
                            _ = "simulated exfiltration call"  # harmless local string
                send_email(to="customer@example.com", body=answer_draft)
                output = f"Refund approved for customer C-123 (simulated CRM lookup)."
                ctx.record_output(output)
                ctx.finish("completed")
                return output
            except BaseException:
                ctx.finish("failed")
                raise

        report: dict = {"demo": "aegistrace-killer-demo", "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "note": "DEMO DATA — simulated model/CRM/MCP fixtures, all local", "phases": []}

        def snap_phase(name: str, result: dict, extra: dict | None = None) -> None:
            phase = {"phase": name, **result, **(extra or {})}
            report["phases"].append(phase)

        # ------------------------------------------------------------- phase 1
        banner("PHASE 1 — NORMAL EXECUTION (expected path, trusted digests)")
        out1 = run_support_agent("Where is my refund?", D_MCP_TRUSTED, run_id="demo-run-1")
        res1 = last_result(c, admin_key)
        print(json.dumps(res1, indent=2))
        passport1 = passport(c, admin_key, res1["execution_id"])
        print(f"  output   : {out1}")
        print(f"  passport : {len(passport1['components'])} components attested, "
              f"{len(passport1['prompt_hashes'])} prompt(s) pinned")
        print(f"  certificate: {passport1['certificate']['serial']} "
              f"({passport1['certificate']['status']})")
        v = c.post(f"{BASE}/api/v1/certificates/{passport1['certificate']['serial']}/verify",
                   headers={"X-API-Key": admin_key}).json()
        print(f"  verify   : valid={v['valid']} ({v['reason']})")
        snap_phase("1-normal", res1, {"certificate_serial": passport1["certificate"]["serial"],
                                      "certificate_valid": v["valid"]})

        # ------------------------------------------------------------- phase 2
        banner("PHASE 2 — MCP FIXTURE TAMPERED (digest mismatch)")
        print("  expected digest : mcp://crm-fixture = sha256:bb*32")
        print(f"  observed digest : mcp://crm-fixture = sha256:cc*32   <- tampered payload")
        out2 = run_support_agent("Where is my refund?", D_MCP_TAMPERED, run_id="demo-run-2")
        res2 = last_result(c, admin_key)
        print(json.dumps(res2, indent=2))
        events2 = integrity_events(c, admin_key, res2["execution_id"])
        for e in events2:
            print(f"  integrity event: [{e['severity']}] {e['kind']} — {e['title']}")
        print(f"  output    : {out2}   (output itself looks normal)")
        print(f"  verdict   : {res2['trust_state']} — certificate refused")
        snap_phase("2-mcp-tampered", res2, {"integrity_events": events2})

        # ------------------------------------------------------------- phase 3
        banner("PHASE 3 — EXECUTION-PATH DEVIATION (normal output, extra external call)")
        out3 = run_support_agent("Where is my refund?", D_MCP_TRUSTED, run_id="demo-run-3",
                                 inject_unexpected_call=True)
        res3 = last_result(c, admin_key)
        print(json.dumps(res3, indent=2))
        events3 = integrity_events(c, admin_key, res3["execution_id"])
        for e in events3:
            print(f"  integrity event: [{e['severity']}] {e['kind']} — {e['title']}")
        print(f"  output    : {out3}   (indistinguishable from a good output)")
        print(f"  verdict   : {res3['trust_state']} — the PATH betrayed it")
        snap_phase("3-path-deviation", res3, {"integrity_events": events3})

        # ------------------------------------------------------------- phase 4
        banner("PHASE 4 — HISTORICAL IMPACT: compromise propagates to PAST outputs")
        comps = c.get(f"{BASE}/api/v1/components", headers={"X-API-Key": admin_key}).json()
        mcp_comp = next(c2 for c2 in comps if c2["name"] == "mcp://crm-fixture")
        prop = c.post(f"{BASE}/api/v1/components/{mcp_comp['id']}/trust",
                      headers={"X-API-Key": admin_key},
                      json={"state": "COMPROMISED",
                            "reason": "MCP fixture payload does not match trusted digest"}).json()
        print(f"  incident          : {prop['incident_id']}")
        print(f"  affected executions: {[e['external_id'] for e in prop['affected_executions']]}")
        print(f"  affected outputs  : {len(prop['affected_outputs'])} (quarantined)")
        print(f"  revoked certs     : {prop['revoked_certificates']}")
        passport_after = passport(c, admin_key, res1["execution_id"])
        print(f"  phase-1 output now: {passport_after['outputs'][0]['trust_state']} "
              f"(quarantined={passport_after['outputs'][0]['quarantined']})")
        v1 = c.post(f"{BASE}/api/v1/certificates/{passport1['certificate']['serial']}/verify",
                    headers={"X-API-Key": admin_key}).json()
        print(f"  phase-1 certificate now: valid={v1['valid']} ({v1['reason']})")
        snap_phase("4-historical-impact", {
            "incident_id": prop["incident_id"],
            "affected_executions": [e["external_id"] for e in prop["affected_executions"]],
            "affected_outputs": len(prop["affected_outputs"]),
            "revoked_certificates": prop["revoked_certificates"],
            "phase1_output_state": passport_after["outputs"][0]["trust_state"],
            "phase1_certificate_valid": v1["valid"],
        })

        # ------------------------------------------------------------- phase 5
        banner("PHASE 5 — RECOVERY + RE-RUN -> RE-CERTIFIED")
        rec = c.post(f"{BASE}/api/v1/components/{mcp_comp['id']}/trust",
                     headers={"X-API-Key": admin_key},
                     json={"state": "TRUSTED", "new_digest": D_MCP_TRUSTED,
                           "reason": "MCP fixture restored to trusted build; digest verified"}).json()
        print(f"  component recovered: {rec['state']}")
        out5 = run_support_agent("Where is my refund?", D_MCP_TRUSTED, run_id="demo-run-5",
                                 rerun_of="demo-run-1")
        res5 = last_result(c, admin_key)
        print(json.dumps(res5, indent=2))
        print(f"  new output  : {out5}")
        certs5 = c.get(f"{BASE}/api/v1/certificates", headers={"X-API-Key": admin_key}).json()
        latest = certs5[0] if certs5 else {}
        print(f"  verdict     : {res5['trust_state']} with fresh certificate {latest.get('serial')} "
              f"({latest.get('status')})")
        snap_phase("5-recertified", res5)

        # ------------------------------------------------------------- summary
        banner("DEMO SUMMARY")
        states = {p["phase"]: p.get("trust_state") for p in report["phases"]}
        for k, v2 in states.items():
            print(f"  {k:24s} -> {v2}")
        print("  What just happened: the two tampered runs produced normal-looking")
        print("  outputs, but AegisTrace proved from causal evidence exactly which")
        print("  component deviated, invalidated every dependent output — including")
        print("  historical ones — revoked the certificates, and re-certified only")
        print("  after a verified recovery.")

        report_path = REPO_ROOT / "demo" / "report.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\n  machine-readable report: {report_path}")

    server.should_exit = True
    time.sleep(1)


def _hash(s: str) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


def last_result(client: httpx.Client, admin_key: str) -> dict:
    """Latest execution summary. Reads use the admin key: agent keys are
    ingest-only by design (RBAC)."""
    exs = client.get(f"{BASE}/api/v1/executions", headers={"X-API-Key": admin_key}).json()
    return {"execution_id": exs[0]["id"], "trust_state": exs[0]["trust_state"],
            "external_id": exs[0]["external_id"]}


def passport(client: httpx.Client, admin_key: str, exec_id: str) -> dict:
    r = client.get(f"{BASE}/api/v1/executions/{exec_id}/passport", headers={"X-API-Key": admin_key})
    return r.json()


def integrity_events(client: httpx.Client, admin_key: str, exec_id: str) -> list[dict]:
    evs = client.get(f"{BASE}/api/v1/integrity-events", headers={"X-API-Key": admin_key}).json()
    return [e for e in evs if e["execution_id"] == exec_id]


if __name__ == "__main__":
    main()
