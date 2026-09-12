"""Trust engine — explainable trust-state decisions and causal propagation.

Core invariants:
- UNKNOWN != TRUSTED: insufficient evidence never yields TRUSTED.
- Every state change writes a TrustDecision with a full evidence chain.
- Compromise propagates along causal edges (component -> executions -> outputs
  -> certificates) with per-hop evidence recorded for UI/audit.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.domain import models
from backend.app.domain.enums import (
    CertStatus,
    EdgeKind,
    IncidentStatus,
    NodeKind,
    PolicyAction,
    Severity,
    TrustState,
)
from backend.app.policy.engine import effective_rules, severity_rank


def _decision(
    session: Session,
    tenant_id: uuid.UUID,
    subject_kind: NodeKind,
    subject_id: uuid.UUID,
    state: TrustState,
    reason: str,
    evidence: dict,
    decided_by: str = "trust-engine",
) -> models.TrustDecision:
    dec = models.TrustDecision(
        tenant_id=tenant_id, subject_kind=subject_kind, subject_id=subject_id,
        state=state, reason=reason, evidence=evidence, decided_by=decided_by,
    )
    session.add(dec)
    return dec


# --- execution trust decision ------------------------------------------------


def get_default_policy(session: Session, tenant_id: uuid.UUID) -> models.Policy:
    """Per-tenant default policy row; created on first use with default rules."""
    pol = session.execute(
        select(models.Policy).where(models.Policy.tenant_id == tenant_id,
                                    models.Policy.is_default.is_(True))
    ).scalars().first()
    if pol is None:
        from backend.app.policy.engine import DEFAULT_RULES
        pol = models.Policy(tenant_id=tenant_id, name="default",
                            rules=dict(DEFAULT_RULES), is_default=True)
        session.add(pol)
        session.flush()
    return pol


def decide_execution(
    session: Session,
    tenant_id: uuid.UUID,
    execution: models.Execution,
    deviations: list[dict],
    integrity_event_ids: list[uuid.UUID],
    policy_rules: dict | None = None,
    baseline: models.Baseline | None = None,
    cert_issuer: Callable | None = None,
) -> TrustState:
    """Map deviations -> trust state per policy; update outputs; maybe certify."""
    rules = effective_rules(policy_rules)
    severity_name: str | None = None
    if not (execution.steps or []):
        # no evidence at all: collector down / events lost -> UNKNOWN, never DEGRADED
        new_state = TrustState.UNKNOWN
        reason = "No provenance steps recorded (missing evidence)"
    elif deviations:
        worst = max((severity_rank(d["severity"]) for d in deviations))
        severity_name = [s.value for s in Severity][worst]
        new_state = TrustState(rules.get(severity_name, TrustState.DEGRADED.value))
        reason = f"{len(deviations)} integrity deviation(s); worst severity {severity_name}"
    elif baseline is None:
        new_state = TrustState(rules.get("no_baseline", TrustState.UNKNOWN.value))
        reason = "No expected-state baseline registered for this agent"
    else:
        new_state = TrustState.TRUSTED
        reason = "All baseline checks passed (digests, path, allow-lists)"

    evidence = {
        "severity_worst": severity_name,
        "integrity_event_ids": [str(i) for i in integrity_event_ids],
        "deviations": deviations,
        "baseline_id": str(baseline.id) if baseline else None,
        "fingerprint": execution.fingerprint,
        "policy_rules": {k: v for k, v in rules.items() if k in
                         ("critical", "high", "medium", "low", "no_baseline")},
    }

    # a re-run after recovery that passes all checks is RE-CERTIFIED
    if new_state == TrustState.TRUSTED and (execution.meta or {}).get("rerun_of"):
        new_state = TrustState.RE_CERTIFIED
        reason = "Re-run after recovery passed all baseline checks (re-certification)"

    execution.trust_state = new_state
    _decision(session, tenant_id, NodeKind.EXECUTION, execution.id, new_state, reason, evidence)

    # outputs inherit the execution's trust state (+ quarantine per policy)
    outputs = session.execute(
        select(models.Output).where(models.Output.tenant_id == tenant_id,
                                    models.Output.execution_id == execution.id)
    ).scalars().all()
    for out in outputs:
        out.trust_state = new_state
        if new_state == TrustState.UNTRUSTED and rules.get("quarantine_outputs", True):
            out.quarantined = True
            session.add(models.QuarantineAction(
                tenant_id=tenant_id, target_kind=NodeKind.OUTPUT, target_id=out.id,
                action=PolicyAction.QUARANTINE,
                result=f"Output quarantined: {reason}",
            ))

    # issue certificate for trusted completed executions
    if cert_issuer is not None and rules.get("certify_trusted", True) \
            and new_state in (TrustState.TRUSTED, TrustState.RE_CERTIFIED) \
            and execution.status.value == "completed":
        cert_issuer(execution, new_state, reason, evidence)

    return new_state


# --- compromise propagation ----------------------------------------------------


def _executions_using_component(session: Session, tenant_id: uuid.UUID, component_id: uuid.UUID,
                                since=None) -> list[models.Execution]:
    stmt = (
        select(models.Execution)
        .join(models.Edge, models.Edge.src_id == models.Execution.id)
        .where(
            models.Edge.tenant_id == tenant_id,
            models.Edge.src_kind == NodeKind.EXECUTION,
            models.Edge.dst_kind == NodeKind.COMPONENT,
            models.Edge.dst_id == component_id,
            models.Edge.kind == EdgeKind.STEP,
        )
    )
    if since is not None:
        stmt = stmt.where(models.Edge.ts >= since)
    return list(session.execute(stmt).scalars().all())


def compromise_component(
    session: Session,
    tenant_id: uuid.UUID,
    component: models.Component,
    reason: str,
    compromised_since=None,
    actor: str = "trust-engine",
) -> dict:
    """Mark a component COMPROMISED and propagate through the causal graph.

    Returns an explainable summary: affected executions/outputs/certificates with
    the evidence chain for each.
    """
    rules = effective_rules(None)
    component.trust_state = TrustState.COMPROMISED
    component.state_reason = reason
    component.state_updated_at = models.utcnow()

    incident = models.Incident(
        tenant_id=tenant_id,
        title=f"Compromised {component.kind.value}: {component.name}",
        severity=Severity.CRITICAL,
        status=IncidentStatus.CONTAINED,
        root_component_id=component.id,
        description=reason,
        evidence={"component_id": str(component.id), "expected_digest": component.digest_expected,
                  "observed_digest": component.digest_observed},
    )
    session.add(incident)
    session.flush()

    propagation_scope = rules.get("compromised_propagation", "all_history")
    since = compromised_since if propagation_scope == "from_compromise_time" else None
    executions = _executions_using_component(session, tenant_id, component.id, since=since)

    affected_executions: list[dict] = []
    affected_outputs: list[dict] = []
    revoked_certs: list[str] = []

    for ex in executions:
        chain = [
            {"hop": 1, "from": f"component:{component.kind.value}:{component.name}",
             "to": f"execution:{ex.external_id}", "edge": EdgeKind.STEP.value,
             "evidence": "causal edge recorded at ingestion"},
        ]
        if ex.trust_state not in (TrustState.UNTRUSTED, TrustState.COMPROMISED):
            ex.trust_state = TrustState.UNTRUSTED
            _decision(session, tenant_id, NodeKind.EXECUTION, ex.id, TrustState.UNTRUSTED,
                      f"Used compromised component {component.kind.value}:{component.name}: {reason}",
                      {"chain": chain, "incident_id": str(incident.id)}, decided_by=actor)
            session.add(models.QuarantineAction(
                tenant_id=tenant_id, incident_id=incident.id,
                target_kind=NodeKind.EXECUTION, target_id=ex.id,
                action=PolicyAction.INVALIDATE, result=f"Execution invalidated: {reason}",
            ))
        affected_executions.append({"execution_id": str(ex.id), "external_id": ex.external_id,
                                    "state": ex.trust_state.value, "chain": chain})

        outputs = session.execute(
            select(models.Output).where(models.Output.tenant_id == tenant_id,
                                        models.Output.execution_id == ex.id)
        ).scalars().all()
        for out in outputs:
            out_chain = chain + [
                {"hop": 2, "from": f"execution:{ex.external_id}",
                 "to": f"output:{out.external_id}", "edge": EdgeKind.PRODUCED.value,
                 "evidence": "output produced by execution"},
            ]
            out.trust_state = TrustState.UNTRUSTED
            out.quarantined = bool(rules.get("quarantine_outputs", True))
            _decision(session, tenant_id, NodeKind.OUTPUT, out.id, TrustState.UNTRUSTED,
                      f"Depends on compromised component {component.name}: {reason}",
                      {"chain": out_chain, "incident_id": str(incident.id)}, decided_by=actor)
            if out.quarantined:
                session.add(models.QuarantineAction(
                    tenant_id=tenant_id, incident_id=incident.id,
                    target_kind=NodeKind.OUTPUT, target_id=out.id,
                    action=PolicyAction.QUARANTINE, result=f"Output quarantined: {reason}",
                ))
            affected_outputs.append({"output_id": str(out.id), "external_id": out.external_id,
                                     "digest": out.digest, "chain": out_chain})

        certs = session.execute(
            select(models.Certificate).where(
                models.Certificate.tenant_id == tenant_id,
                models.Certificate.execution_id == ex.id,
                models.Certificate.status == CertStatus.ACTIVE,
            )
        ).scalars().all()
        for cert in certs:
            cert.status = CertStatus.REVOKED
            cert.revoked_reason = f"Dependency compromised: {component.name}: {reason}"
            revoked_certs.append(cert.serial)

    incident.evidence = {
        **incident.evidence,
        "affected_executions": affected_executions,
        "affected_outputs": affected_outputs,
        "revoked_certificates": revoked_certs,
    }

    return {
        "incident_id": str(incident.id),
        "component": {"id": str(component.id), "kind": component.kind.value, "name": component.name},
        "affected_executions": affected_executions,
        "affected_outputs": affected_outputs,
        "revoked_certificates": revoked_certs,
    }


def recover_component(
    session: Session,
    tenant_id: uuid.UUID,
    component: models.Component,
    reason: str,
    new_digest: str | None = None,
    actor: str = "operator",
) -> dict:
    """Restore a component to TRUSTED (with verified digest). Historical outputs
    stay untrusted — recovery enables re-execution, not silent re-trusting."""
    component.trust_state = TrustState.TRUSTED
    component.state_reason = reason
    if new_digest:
        component.digest_expected = new_digest
        component.digest_observed = new_digest
    component.state_updated_at = models.utcnow()

    open_incidents = session.execute(
        select(models.Incident).where(
            models.Incident.tenant_id == tenant_id,
            models.Incident.root_component_id == component.id,
            models.Incident.status != IncidentStatus.RESOLVED,
        )
    ).scalars().all()
    for inc in open_incidents:
        inc.status = IncidentStatus.RECOVERING
        inc.evidence = {**inc.evidence, "recovery": reason}

    _decision(session, tenant_id, NodeKind.COMPONENT, component.id, TrustState.TRUSTED,
              f"Recovered: {reason}", {"new_digest": new_digest}, decided_by=actor)
    session.add(models.QuarantineAction(
        tenant_id=tenant_id,
        target_kind=NodeKind.COMPONENT, target_id=component.id,
        action=PolicyAction.RERUN,
        result="Component recovered; re-execution required to re-certify outputs",
    ))
    return {"component_id": str(component.id), "state": component.trust_state.value,
            "recovered_incidents": [str(i.id) for i in open_incidents]}


def component_impact(session: Session, tenant_id: uuid.UUID, component: models.Component) -> dict:
    """Answer: 'What outputs depended on this component?' (live view)."""
    executions = _executions_using_component(session, tenant_id, component.id)
    exec_view: list[dict] = []
    output_view: list[dict] = []
    for ex in executions:
        exec_view.append({"execution_id": str(ex.id), "external_id": ex.external_id,
                          "trust_state": ex.trust_state.value, "agent_ref": ex.agent_ref,
                          "started_at": ex.started_at.isoformat()})
        outputs = session.execute(
            select(models.Output).where(models.Output.tenant_id == tenant_id,
                                        models.Output.execution_id == ex.id)
        ).scalars().all()
        for out in outputs:
            output_view.append({"output_id": str(out.id), "external_id": out.external_id,
                                "execution_id": str(ex.id), "trust_state": out.trust_state.value,
                                "quarantined": out.quarantined, "digest": out.digest})
    certs = session.execute(
        select(models.Certificate).where(models.Certificate.tenant_id == tenant_id,
                                         models.Certificate.execution_id.in_([e.id for e in executions] or [uuid.uuid4()]))
    ).scalars().all()
    return {
        "component": {"id": str(component.id), "kind": component.kind.value, "name": component.name,
                      "trust_state": component.trust_state.value},
        "executions": exec_view,
        "outputs": output_view,
        "certificates": [{"serial": c.serial, "status": c.status.value,
                          "revoked_reason": c.revoked_reason} for c in certs],
    }
