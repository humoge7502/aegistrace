"""Graph service — provenance ingestion into the relational causal graph and
expected-vs-observed deviation detection.

This module is the core of the P0 thesis:
  observed events -> components/edges/steps -> fingerprint -> baseline comparison
  -> integrity events -> (trust engine takes over).
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.crypto import canonical_json
from backend.app.core.security import redact_strings
from backend.app.domain import models
from backend.app.domain.enums import (
    ComponentKind,
    EdgeKind,
    ExecutionStatus,
    FingerprintMode,
    IntegrityKind,
    NodeKind,
    Severity,
    StepKind,
    TrustState,
)


# --- helpers -----------------------------------------------------------------


def _parse_ts(ts: str | None) -> datetime:
    if ts:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
    return models.utcnow()


def upsert_component(
    session: Session,
    tenant_id: uuid.UUID,
    kind: str,
    name: str,
    version: str | None = None,
    digest_observed: str | None = None,
    meta: dict | None = None,
) -> models.Component:
    ck = ComponentKind(kind)
    stmt = select(models.Component).where(
        models.Component.tenant_id == tenant_id,
        models.Component.kind == ck,
        models.Component.name == name,
        models.Component.version == version,
    )
    comp = session.execute(stmt).scalar_one_or_none()
    if comp is None:
        comp = models.Component(
            tenant_id=tenant_id, kind=ck, name=name, version=version,
            trust_state=TrustState.UNKNOWN, meta=redact_strings(meta or {}),
        )
        session.add(comp)
        session.flush()
    if digest_observed:
        comp.digest_observed = digest_observed
    return comp


def get_execution_by_external(session: Session, tenant_id: uuid.UUID, external_id: str) -> models.Execution | None:
    return session.execute(
        select(models.Execution).where(
            models.Execution.tenant_id == tenant_id,
            models.Execution.external_id == external_id,
        )
    ).scalar_one_or_none()


def record_step(
    session: Session,
    tenant_id: uuid.UUID,
    execution: models.Execution,
    payload: dict,
) -> None:
    """Record a completed step: component + ordered causal edge + step entry."""
    seq = int(payload.get("seq") or (len(execution.steps) + 1))
    kind = payload.get("kind") or StepKind.CUSTOM.value
    target = payload.get("target") or "unknown"
    digest = payload.get("digest")
    comp = upsert_component(
        session, tenant_id,
        kind=_component_kind_for_step(kind),
        name=target,
        version=payload.get("version"),
        digest_observed=digest,
        meta=payload.get("meta"),
    )
    # reassign (don't append in place): SQLAlchemy tracks reassigned JSON columns
    steps = list(execution.steps or [])
    steps.append({
        "seq": seq,
        "kind": kind,
        "target": target,
        "digest": digest,
        "component_id": str(comp.id),
        "ts": payload.get("ts"),
        "meta": redact_strings(payload.get("meta") or {}),
    })
    execution.steps = steps
    session.add(models.Edge(
        tenant_id=tenant_id,
        src_kind=NodeKind.EXECUTION, src_id=execution.id,
        dst_kind=NodeKind.COMPONENT, dst_id=comp.id,
        kind=EdgeKind.STEP, execution_id=execution.id, seq=seq,
        expected=True, ts=_parse_ts(payload.get("ts")),
    ))


def _component_kind_for_step(kind: str) -> str:
    mapping = {
        StepKind.MODEL.value: ComponentKind.MODEL.value,
        StepKind.RETRIEVAL.value: ComponentKind.CORPUS.value,
        StepKind.TOOL.value: ComponentKind.TOOL.value,
        StepKind.MCP.value: ComponentKind.MCP_SERVER.value,
        StepKind.API.value: ComponentKind.API.value,
        StepKind.EMBEDDING.value: ComponentKind.EMBEDDING_MODEL.value,
        StepKind.RUNTIME.value: ComponentKind.RUNTIME.value,
        StepKind.PACKAGE.value: ComponentKind.PACKAGE.value,
    }
    return mapping.get(kind, ComponentKind.EXTERNAL_SERVICE.value)


def record_output(
    session: Session,
    tenant_id: uuid.UUID,
    execution: models.Execution,
    payload: dict,
) -> models.Output:
    out = models.Output(
        tenant_id=tenant_id,
        execution_id=execution.id,
        external_id=payload.get("output_id") or f"out-{uuid.uuid4().hex[:12]}",
        kind=payload.get("output_kind", "text"),
        digest=payload.get("digest") or hash_content(payload.get("content", "")),
        trust_state=TrustState.UNKNOWN,
    )
    session.add(out)
    session.flush()
    session.add(models.Edge(
        tenant_id=tenant_id,
        src_kind=NodeKind.EXECUTION, src_id=execution.id,
        dst_kind=NodeKind.OUTPUT, dst_id=out.id,
        kind=EdgeKind.PRODUCED, execution_id=execution.id,
        expected=True, ts=_parse_ts(payload.get("ts")),
    ))
    return out


def hash_content(content) -> str:
    if isinstance(content, str):
        data = content.encode("utf-8")
    elif isinstance(content, (dict, list)):
        data = canonical_json(content)
    else:
        data = str(content).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def fingerprint_of(steps: list[dict]) -> str:
    """Canonical execution fingerprint: sha256 over ordered step signatures."""
    sig = [{"kind": s.get("kind"), "target": s.get("target"), "digest": s.get("digest")}
           for s in sorted(steps, key=lambda x: x.get("seq", 0))]
    return "sha256:" + hashlib.sha256(canonical_json(sig)).hexdigest()


# --- baseline comparison ------------------------------------------------------


def compare_baseline(baseline_doc: dict, mode: str, execution: models.Execution) -> list[dict]:
    """Return deviation dicts: {kind, severity, title, expected, observed}."""
    deviations: list[dict] = []
    steps = sorted(execution.steps, key=lambda s: s.get("seq", 0))
    expected_steps: list[dict] = sorted(baseline_doc.get("steps", []), key=lambda s: s.get("seq", 0))
    allowed: dict[str, list[str]] = baseline_doc.get("allowed", {})
    component_digests: dict[str, str] = baseline_doc.get("component_digests", {})

    # 1. digest verification for every observed component
    for s in steps:
        exp_digest = component_digests.get(s.get("target", ""))
        if exp_digest and s.get("digest") and s["digest"] != exp_digest:
            deviations.append({
                "kind": IntegrityKind.DIGEST_MISMATCH.value,
                "severity": Severity.CRITICAL.value,
                "title": f"Digest mismatch for {s.get('target')}",
                "expected": {"target": s.get("target"), "digest": exp_digest},
                "observed": {"target": s.get("target"), "digest": s.get("digest")},
            })

    if mode == FingerprintMode.POLICY_ONLY.value:
        return deviations

    # 2. component allow-lists (allowed_set and sequence modes)
    for s in steps:
        kind, target = s.get("kind", ""), s.get("target", "")
        allowed_targets = allowed.get(f"{kind}s") or allowed.get(kind) or []
        if allowed_targets and target not in allowed_targets:
            deviations.append({
                "kind": IntegrityKind.UNEXPECTED_COMPONENT.value,
                "severity": Severity.CRITICAL.value,
                "title": f"Unexpected {kind} component: {target}",
                "expected": {"allowed": allowed_targets},
                "observed": {"kind": kind, "target": target},
            })

    # 3. path comparison
    if mode == FingerprintMode.SEQUENCE.value:
        exp_path = [(s.get("kind"), s.get("target")) for s in expected_steps]
        obs_path = [(s.get("kind"), s.get("target")) for s in steps]
        if exp_path and obs_path and exp_path != obs_path:
            deviations.append({
                "kind": IntegrityKind.PATH_DEVIATION.value,
                "severity": Severity.HIGH.value,
                "title": "Execution path deviated from baseline sequence",
                "expected": {"path": [list(p) for p in exp_path]},
                "observed": {"path": [list(p) for p in obs_path]},
            })
        exp_pairs = set(exp_path)
        for s in steps:
            if (s.get("kind"), s.get("target")) not in exp_pairs:
                deviations.append({
                    "kind": IntegrityKind.UNEXPECTED_COMPONENT.value,
                    "severity": Severity.CRITICAL.value,
                    "title": f"Component not in expected path: {s.get('target')}",
                    "expected": {"path": [list(p) for p in exp_path]},
                    "observed": {"kind": s.get("kind"), "target": s.get("target")},
                })
        obs_pairs = set(obs_path)
        for e in expected_steps:
            if (e.get("kind"), e.get("target")) not in obs_pairs:
                deviations.append({
                    "kind": IntegrityKind.MISSING_STEP.value,
                    "severity": Severity.MEDIUM.value,
                    "title": f"Expected step missing: {e.get('target')}",
                    "expected": {"kind": e.get("kind"), "target": e.get("target")},
                    "observed": None,
                })

    # 4. prompt pinning
    prompt_hashes: dict[str, str] = baseline_doc.get("prompt_hashes", {})
    if prompt_hashes:
        observed_prompts = (execution.meta or {}).get("prompt_hashes", {})
        for role, digest in prompt_hashes.items():
            obs = observed_prompts.get(role)
            if obs and obs != digest:
                deviations.append({
                    "kind": IntegrityKind.PROMPT_MISMATCH.value,
                    "severity": Severity.CRITICAL.value,
                    "title": f"Prompt hash mismatch ({role})",
                    "expected": {"role": role, "hash": digest},
                    "observed": {"role": role, "hash": obs},
                })

    # deduplicate (kind,target,title)
    seen: set[tuple] = set()
    unique: list[dict] = []
    for d in deviations:
        key = (d["kind"], d.get("observed", {}).get("target") if d.get("observed") else None, d["title"])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def finish_execution(session: Session, tenant_id: uuid.UUID, execution: models.Execution) -> None:
    """Freeze the execution, compute the fingerprint, and record deviations."""
    execution.status = ExecutionStatus(event_payload_status(execution))
    execution.fingerprint = fingerprint_of(execution.steps)
    execution.finished_at = models.utcnow()

    if not execution.steps:
        session.add(models.IntegrityEvent(
            tenant_id=tenant_id, execution_id=execution.id,
            kind=IntegrityKind.MISSING_PROVENANCE, severity=Severity.MEDIUM,
            title="Execution finished with no provenance steps",
            expected={"steps": "> 0"}, observed={"steps": 0},
            evidence={"fingerprint": execution.fingerprint},
        ))


def event_payload_status(execution: models.Execution) -> str:
    # finished executions default to completed; failures arrive via payload
    return ExecutionStatus.COMPLETED.value if execution.status == ExecutionStatus.RUNNING.value else execution.status.value
