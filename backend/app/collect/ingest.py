"""Event ingestion dispatcher: raw events -> graph -> deviations -> trust decisions.

One transaction per batch; a bad event fails the batch with a 422 naming the
index (clients can resend; RawEvent is append-only for replay).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.domain.enums import (
    EdgeKind,
    EventKind,
    ExecutionStatus,
    IntegrityKind,
    NodeKind,
    Severity,
    TrustState,
)
from backend.app.certs import service as cert_service
from backend.app.collect.schemas import EventIn
from backend.app.core.config import get_settings
from backend.app.core.security import CONTENT_KEYS, hash_content_value, redact_strings
from backend.app.domain import models
from backend.app.graph import service as graph
from backend.app.trust import engine as trust


def sanitize_payload(payload: dict, allow_content: bool) -> dict:
    """Defense in depth (ADR-005): secret-pattern strings are always redacted;
    raw content under CONTENT_KEYS is hashed unless the operator has explicitly
    enabled AEGISTRACE_ALLOW_CONTENT. Already-hashed values pass through."""
    def clean(node):
        if isinstance(node, str):
            return node if node.startswith("sha256:") else hash_content_value(node)
        if isinstance(node, dict):
            return {k: clean(v) for k, v in node.items()}
        if isinstance(node, list):
            return [clean(v) for v in node]
        return node

    def walk(node):
        if isinstance(node, dict):
            return {k: clean(v) if k in CONTENT_KEYS else walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        return node

    out = redact_strings(payload)
    if allow_content:
        return out
    return walk(out)


def process_event(session: Session, tenant_id: uuid.UUID, event: EventIn,
                  signing_key, key_id: str, tenant_name: str) -> dict:
    """Apply one event; returns a small acknowledgement dict."""
    payload = sanitize_payload(event.payload or {}, get_settings().allow_content)
    kind = EventKind(event.kind)

    session.add(models.RawEvent(
        tenant_id=tenant_id,
        execution_external_id=event.execution_external_id,
        kind=kind, payload=payload,
    ))

    if kind == EventKind.EXECUTION_STARTED:
        result = _on_execution_started(session, tenant_id, event, payload)
        session.flush()
        return result
    if kind in (EventKind.STEP_ENDED, EventKind.STEP_STARTED):
        result = _on_step(session, tenant_id, event, payload, ended=(kind == EventKind.STEP_ENDED))
        session.flush()
        return result
    if kind == EventKind.COMPONENT_OBSERVED:
        result = _on_component_observed(session, tenant_id, event, payload)
        session.flush()
        return result
    if kind == EventKind.OUTPUT_PRODUCED:
        result = _on_output(session, tenant_id, event, payload)
        session.flush()
        return result
    if kind == EventKind.PROMPT_PINNED:
        result = _on_prompt(session, tenant_id, event, payload)
        session.flush()
        return result
    if kind == EventKind.EXECUTION_FINISHED:
        result = _on_execution_finished(session, tenant_id, event, payload, signing_key, key_id, tenant_name)
        session.flush()
        return result
    session.flush()
    raise ValueError(f"unhandled event kind {kind}")


def _require_execution(session: Session, tenant_id: uuid.UUID, event: EventIn) -> models.Execution:
    if not event.execution_external_id:
        raise ValueError("execution_external_id required for this event kind")
    ex = graph.get_execution_by_external(session, tenant_id, event.execution_external_id)
    if ex is None:
        raise ValueError(f"unknown execution {event.execution_external_id} (send execution.started first)")
    return ex


def _on_execution_started(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict) -> dict:
    external_id = event.execution_external_id or payload.get("run_id")
    if not external_id:
        raise ValueError("execution.started requires execution_external_id")
    agent_ref = payload.get("agent_ref", "unknown-agent")
    agent_version = payload.get("agent_version")
    existing = graph.get_execution_by_external(session, tenant_id, external_id)
    if existing is not None:
        return {"execution_id": str(existing.id), "deduplicated": True}
    baseline = session.execute(
        select(models.Baseline).where(
            models.Baseline.tenant_id == tenant_id,
            models.Baseline.agent_ref == agent_ref,
            models.Baseline.active.is_(True),
        ).order_by(models.Baseline.created_at.desc())
    ).scalars().first()
    ex = models.Execution(
        tenant_id=tenant_id,
        external_id=external_id,
        baseline_id=baseline.id if baseline else None,
        agent_ref=agent_ref,
        agent_version=agent_version,
        meta={"prompt_hashes": {}, "rerun_of": payload.get("rerun_of")},
    )
    session.add(ex)
    session.flush()

    # pre-register expected components (with expected digests) from the baseline
    if baseline is not None:
        digests = baseline.doc.get("component_digests", {})
        for step in baseline.doc.get("steps", []):
            target = step.get("target")
            if not target:
                continue
            comp = graph.upsert_component(
                session, tenant_id,
                kind=graph._component_kind_for_step(step.get("kind", "custom")),
                name=target, version=step.get("version"),
                digest_observed=None,
            )
            expected = digests.get(target) or step.get("digest")
            if expected and not comp.digest_expected:
                comp.digest_expected = expected
    return {"execution_id": str(ex.id), "baseline_id": str(baseline.id) if baseline else None,
            "baseline_found": baseline is not None}


def _on_step(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict, ended: bool) -> dict:
    # only step.ended contributes to the observed path; step.started is stored
    # in the raw log only (prevents double-recording and premature accounting)
    _require_execution(session, tenant_id, event)
    if not ended:
        return {"recorded": False, "reason": "step.started kept in raw log only; send step.ended to record"}
    ex = _require_execution(session, tenant_id, event)
    graph.record_step(session, tenant_id, ex, payload)
    return {"recorded": True, "steps": len(ex.steps)}


def _on_component_observed(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict) -> dict:
    comp = graph.upsert_component(
        session, tenant_id,
        kind=payload.get("kind", "external_service"),
        name=payload.get("name") or payload.get("target") or "unknown",
        version=payload.get("version"),
        digest_observed=payload.get("digest"),
        meta=payload.get("meta"),
    )
    if event.execution_external_id:
        ex = _require_execution(session, tenant_id, event)
        session.add(models.Edge(
            tenant_id=tenant_id,
            src_kind=NodeKind.EXECUTION, src_id=ex.id,
            dst_kind=NodeKind.COMPONENT, dst_id=comp.id,
            kind=EdgeKind.STEP, execution_id=ex.id,
        ))
    return {"component_id": str(comp.id)}


def _on_output(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict) -> dict:
    ex = _require_execution(session, tenant_id, event)
    out = graph.record_output(session, tenant_id, ex, payload)
    return {"output_id": str(out.id), "digest": out.digest}


def _on_prompt(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict) -> dict:
    ex = _require_execution(session, tenant_id, event)
    role = payload.get("role", "user")
    digest = payload.get("hash")
    if not digest:
        raise ValueError("prompt.pinned requires hash")
    meta = dict(ex.meta or {})
    hashes = dict(meta.get("prompt_hashes", {}))
    hashes[role] = digest
    meta["prompt_hashes"] = hashes
    ex.meta = meta
    return {"pinned": role}


def _on_execution_finished(session: Session, tenant_id: uuid.UUID, event: EventIn, payload: dict,
                           signing_key, key_id: str, tenant_name: str) -> dict:
    external_id = event.execution_external_id or payload.get("execution_external_id")
    if not external_id:
        raise ValueError("execution.finished requires execution_external_id (envelope or payload)")
    ex = graph.get_execution_by_external(session, tenant_id, external_id)
    if ex is None:
        raise ValueError(f"unknown execution {external_id}")
    if ex.finished_at is not None:
        return {"execution_id": str(ex.id), "trust_state": ex.trust_state.value,
                "deviations": 0, "certificate": None, "deduplicated": True}
    if payload.get("status") == "failed":
        ex.status = ExecutionStatus.FAILED

    baseline = session.get(models.Baseline, ex.baseline_id) if ex.baseline_id else None
    policy = trust.get_default_policy(session, tenant_id)
    graph.finish_execution(session, tenant_id, ex)

    deviations: list[dict] = []
    if baseline is not None and ex.status != ExecutionStatus.FAILED:
        deviations = graph.compare_baseline(baseline.doc, baseline.mode.value, ex)

    event_ids: list[uuid.UUID] = []
    for d in deviations:
        ie = models.IntegrityEvent(
            tenant_id=tenant_id, execution_id=ex.id,
            kind=IntegrityKind(d["kind"]),
            severity=Severity(d["severity"]),
            title=d["title"], expected=d.get("expected"), observed=d.get("observed"),
            evidence={"fingerprint": ex.fingerprint},
        )
        session.add(ie)
        session.flush()
        event_ids.append(ie.id)

    def _issue_cert(target_execution: models.Execution, state: TrustState, reason: str, evidence: dict):
        return cert_service.issue_certificate(
            session, tenant_id, target_execution, state, reason, evidence,
            signing_key=signing_key, key_id=key_id, tenant_name=tenant_name,
        )

    state = trust.decide_execution(
        session, tenant_id, ex, deviations, event_ids,
        policy_rules=policy.rules, baseline=baseline, cert_issuer=_issue_cert,
    )
    cert_serial = None
    if state in (TrustState.TRUSTED, TrustState.RE_CERTIFIED):
        cert = session.execute(
            select(models.Certificate).where(
                models.Certificate.tenant_id == tenant_id,
                models.Certificate.execution_id == ex.id,
            ).order_by(models.Certificate.issued_at.desc())
        ).scalars().first()
        cert_serial = cert.serial if cert else None
    return {"execution_id": str(ex.id), "trust_state": state.value,
            "deviations": len(deviations), "certificate": cert_serial}
