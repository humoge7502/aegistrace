"""REST API v1 — provenance, graph, trust, certificates, incidents, policies, audit."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_auth, get_db, require_role, tenant_uuid
from backend.app.certs import service as cert_service
from backend.app.collect.schemas import (
    ApiKeyCreateIn,
    BaselineIn,
    EventBatchIn,
    IncidentActionIn,
    TrustChangeIn,
)
from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
from backend.app.domain import models
from backend.app.domain.enums import (
    EdgeKind,
    FingerprintMode,
    IncidentStatus,
    NodeKind,
    Role,
    TrustState,
)
from backend.app.graph import service as graph
from backend.app.policy.engine import effective_rules
from backend.app.trust import engine as trust

router = APIRouter(prefix="/api/v1")

# explicit role sets — agent keys are ingest-only, viewer keys are read-only
READ_ROLES = {Role.ADMIN, Role.OPERATOR, Role.VIEWER}
INGEST_ROLES = {Role.ADMIN, Role.OPERATOR, Role.AGENT}
MUTATE_ROLES = {Role.ADMIN, Role.OPERATOR}


# --- serialization helpers -----------------------------------------------------


def _iso(dt) -> str | None:
    return dt.isoformat() if dt else None


def execution_dict(ex: models.Execution, include_steps: bool = True) -> dict:
    d = {
        "id": str(ex.id),
        "external_id": ex.external_id,
        "agent_ref": ex.agent_ref,
        "agent_version": ex.agent_version,
        "status": ex.status.value,
        "trust_state": ex.trust_state.value,
        "fingerprint": ex.fingerprint,
        "baseline_id": str(ex.baseline_id) if ex.baseline_id else None,
        "started_at": _iso(ex.started_at),
        "finished_at": _iso(ex.finished_at),
        "meta": ex.meta or {},
    }
    if include_steps:
        d["steps"] = ex.steps or []
    return d


def component_dict(c: models.Component) -> dict:
    return {
        "id": str(c.id), "kind": c.kind.value, "name": c.name, "version": c.version,
        "digest_expected": c.digest_expected, "digest_observed": c.digest_observed,
        "trust_state": c.trust_state.value, "state_reason": c.state_reason,
        "state_updated_at": _iso(c.state_updated_at), "meta": c.meta or {},
    }


def integrity_event_dict(e: models.IntegrityEvent) -> dict:
    return {
        "id": str(e.id), "execution_id": str(e.execution_id) if e.execution_id else None,
        "kind": e.kind.value, "severity": e.severity.value, "title": e.title,
        "expected": e.expected, "observed": e.observed, "evidence": e.evidence,
        "created_at": _iso(e.created_at),
    }


def output_dict(o: models.Output) -> dict:
    return {
        "id": str(o.id), "execution_id": str(o.execution_id), "external_id": o.external_id,
        "kind": o.kind, "digest": o.digest, "trust_state": o.trust_state.value,
        "quarantined": o.quarantined, "created_at": _iso(o.created_at),
    }


def incident_dict(i: models.Incident) -> dict:
    return {
        "id": str(i.id), "title": i.title, "severity": i.severity.value,
        "status": i.status.value,
        "root_component_id": str(i.root_component_id) if i.root_component_id else None,
        "description": i.description, "evidence": i.evidence,
        "created_at": _iso(i.created_at), "resolved_at": _iso(i.resolved_at),
    }


def certificate_dict(c: models.Certificate, include_statement: bool = False) -> dict:
    d = {
        "id": str(c.id), "serial": c.serial, "execution_id": str(c.execution_id),
        "status": c.status.value, "alg": c.alg, "key_id": c.key_id,
        "signature": c.signature, "revoked_reason": c.revoked_reason,
        "issued_at": _iso(c.issued_at),
    }
    if include_statement:
        d["statement"] = c.statement
    return d


def _audit(db: Session, auth: dict, request: Request, action: str, obj_kind: str, obj_id: str, detail: dict | None = None):
    db.add(models.AuditLog(
        tenant_id=auth["tenant_id"], actor=auth["key_name"], action=action,
        object_kind=obj_kind, object_id=obj_id, detail=detail or {},
    ))


def _get_execution(db: Session, tenant_id: uuid.UUID, ident: str) -> models.Execution:
    ex = None
    try:
        ex = db.get(models.Execution, uuid.UUID(ident))
    except ValueError:
        pass
    if ex is None or ex.tenant_id != tenant_id:
        ex = ex if (ex and ex.tenant_id == tenant_id) else graph.get_execution_by_external(db, tenant_id, ident)
    if ex is None or ex.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="execution not found")
    return ex


def _get_component(db: Session, tenant_id: uuid.UUID, ident: str) -> models.Component:
    try:
        comp = db.get(models.Component, uuid.UUID(ident))
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid component id")
    if comp is None or comp.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="component not found")
    return comp


# --- ingestion -------------------------------------------------------------------


@router.post("/events/batch", tags=["ingest"])
def ingest_events(
    batch: EventBatchIn,
    request: Request,
    db: Session = Depends(get_db),
    auth: dict = Depends(get_auth),
):
    require_role(auth, allowed=INGEST_ROLES)
    from backend.app.collect.ingest import process_event
    results = []
    for idx, event in enumerate(batch.events):
        try:
            results.append(process_event(
                db, tenant_uuid(auth), event,
                signing_key=request.app.state.signing_key,
                key_id=request.app.state.key_id,
                tenant_name=request.app.state.tenant_names.get(auth["tenant_id"], "unknown"),
            ))
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"event[{idx}]: {e}")
    request.app.state.metrics.bump("events_ingested", len(batch.events))
    return {"accepted": len(results), "results": results}


# --- baselines ---------------------------------------------------------------------


@router.post("/baselines", tags=["baselines"])
def create_baseline(b: BaselineIn, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=MUTATE_ROLES)
    if b.mode not in (m.value for m in FingerprintMode):
        raise HTTPException(status_code=422, detail=f"invalid mode {b.mode}")
    row = models.Baseline(
        tenant_id=tenant_uuid(auth), agent_ref=b.agent_ref, agent_version=b.agent_version,
        mode=FingerprintMode(b.mode),
        doc={"steps": [s.model_dump() for s in b.steps], "allowed": b.allowed,
             "component_digests": b.component_digests, "prompt_hashes": b.prompt_hashes},
    )
    db.add(row)
    db.flush()
    _audit(db, auth, None, "baseline.create", "baseline", str(row.id), {"agent_ref": b.agent_ref})
    return {"id": str(row.id), "agent_ref": row.agent_ref, "mode": row.mode.value}


@router.get("/baselines", tags=["baselines"])
def list_baselines(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    rows = db.execute(
        select(models.Baseline).where(models.Baseline.tenant_id == tenant_uuid(auth))
        .order_by(models.Baseline.created_at.desc())
    ).scalars().all()
    return [{"id": str(b.id), "agent_ref": b.agent_ref, "agent_version": b.agent_version,
             "mode": b.mode.value, "active": b.active, "created_at": _iso(b.created_at),
             "doc": b.doc} for b in rows]


# --- executions ----------------------------------------------------------------------


@router.get("/executions", tags=["executions"])
def list_executions(
    limit: int = 50, offset: int = 0,
    db: Session = Depends(get_db), auth: dict = Depends(get_auth),
):
    require_role(auth, allowed=READ_ROLES)
    q = select(models.Execution).where(models.Execution.tenant_id == tenant_uuid(auth)) \
        .order_by(models.Execution.started_at.desc()).offset(offset).limit(min(limit, 200))
    rows = db.execute(q).scalars().all()
    return [execution_dict(e, include_steps=False) for e in rows]


@router.get("/executions/{ident}", tags=["executions"])
def get_execution(ident: str, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    ex = _get_execution(db, tenant_uuid(auth), ident)
    return execution_dict(ex)


@router.get("/executions/{ident}/passport", tags=["executions"])
def get_passport(ident: str, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    """AI Execution Passport: machine-readable summary of everything that influenced
    this execution plus the trust verdict and its evidence."""
    require_role(auth, allowed=READ_ROLES)
    tenant_id = tenant_uuid(auth)
    ex = _get_execution(db, tenant_id, ident)

    components = []
    for s in ex.steps or []:
        comp = db.get(models.Component, uuid.UUID(s["component_id"])) if s.get("component_id") else None
        components.append({
            "kind": s.get("kind"), "target": s.get("target"), "digest": s.get("digest"),
            "seq": s.get("seq"),
            "trust_state": comp.trust_state.value if comp else TrustState.UNKNOWN.value,
            "digest_expected": comp.digest_expected if comp else None,
            "digest_observed": comp.digest_observed if comp else None,
            "component_id": s.get("component_id"),
        })

    decisions = db.execute(
        select(models.TrustDecision).where(
            models.TrustDecision.tenant_id == tenant_id,
            models.TrustDecision.subject_kind == NodeKind.EXECUTION,
            models.TrustDecision.subject_id == ex.id,
        ).order_by(models.TrustDecision.created_at.desc())
    ).scalars().all()

    outputs = db.execute(
        select(models.Output).where(models.Output.tenant_id == tenant_id,
                                    models.Output.execution_id == ex.id)
    ).scalars().all()

    cert = db.execute(
        select(models.Certificate).where(
            models.Certificate.tenant_id == tenant_id,
            models.Certificate.execution_id == ex.id,
        ).order_by(models.Certificate.issued_at.desc())
    ).scalars().first()

    integrity_events = db.execute(
        select(models.IntegrityEvent).where(
            models.IntegrityEvent.tenant_id == tenant_id,
            models.IntegrityEvent.execution_id == ex.id,
        ).order_by(models.IntegrityEvent.created_at.desc())
    ).scalars().all()

    return {
        "passport_version": "1",
        "execution": execution_dict(ex),
        "prompt_hashes": (ex.meta or {}).get("prompt_hashes", {}),
        "components": components,
        "outputs": [output_dict(o) for o in outputs],
        "trust": {
            "state": ex.trust_state.value,
            "decisions": [{
                "state": d.state.value, "reason": d.reason, "evidence": d.evidence,
                "decided_by": d.decided_by, "created_at": _iso(d.created_at),
            } for d in decisions],
            "integrity_events": [integrity_event_dict(e) for e in integrity_events],
        },
        "certificate": certificate_dict(cert, include_statement=True) if cert else None,
    }


@router.get("/executions/{ident}/graph", tags=["graph"])
def get_execution_graph(ident: str, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    tenant_id = tenant_uuid(auth)
    ex = _get_execution(db, tenant_id, ident)

    edges = db.execute(
        select(models.Edge).where(
            models.Edge.tenant_id == tenant_id, models.Edge.execution_id == ex.id)
    ).scalars().all()

    nodes = [{"id": f"execution:{ex.id}", "type": "execution", "label": ex.external_id,
              "trust_state": ex.trust_state.value, "agent_ref": ex.agent_ref}]
    comp_nodes: dict[str, dict] = {}
    unexpected_targets: set[str] = set()
    mismatch_targets: set[str] = set()
    ievents = db.execute(
        select(models.IntegrityEvent).where(
            models.IntegrityEvent.tenant_id == tenant_id,
            models.IntegrityEvent.execution_id == ex.id)
    ).scalars().all()
    for ie in ievents:
        obs = (ie.observed or {})
        if ie.kind.value in ("unexpected_component", "path_deviation") and obs.get("target"):
            unexpected_targets.add(obs["target"])
        if ie.kind.value in ("digest_mismatch", "prompt_mismatch") and obs.get("target"):
            mismatch_targets.add(obs["target"])

    for e in edges:
        if e.kind == EdgeKind.STEP and e.dst_kind == NodeKind.COMPONENT:
            comp = db.get(models.Component, e.dst_id)
            if comp is None:
                continue
            key = f"component:{comp.id}"
            if key not in comp_nodes:
                comp_nodes[key] = {
                    "id": key, "type": "component", "component_kind": comp.kind.value,
                    "label": comp.name, "version": comp.version,
                    "trust_state": comp.trust_state.value,
                    "digest_observed": comp.digest_observed, "digest_expected": comp.digest_expected,
                    "deviation": comp.name in unexpected_targets or comp.name in mismatch_targets,
                }
        elif e.kind == EdgeKind.PRODUCED:
            out = db.get(models.Output, e.dst_id)
            if out is not None:
                nodes.append({"id": f"output:{out.id}", "type": "output", "label": out.external_id,
                              "trust_state": out.trust_state.value, "quarantined": out.quarantined,
                              "digest": out.digest})

    edge_list = []
    for e in sorted(edges, key=lambda x: (x.seq or 0)):
        edge_list.append({
            "src": f"{e.src_kind.value}:{e.src_id}", "dst": f"{e.dst_kind.value}:{e.dst_id}",
            "kind": e.kind.value, "seq": e.seq, "expected": e.expected,
        })
    # annotate step edges into deviating components as unexpected
    for node in comp_nodes.values():
        if node["deviation"]:
            for el in edge_list:
                if el["dst"] == node["id"] and el["kind"] == "step":
                    el["expected"] = False

    return {"nodes": nodes + list(comp_nodes.values()), "edges": edge_list,
            "integrity_events": [integrity_event_dict(ie) for ie in ievents]}


# --- components & impact ----------------------------------------------------------------


@router.get("/components", tags=["components"])
def list_components(kind: str | None = None, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    q = select(models.Component).where(models.Component.tenant_id == tenant_uuid(auth))
    if kind:
        q = q.where(models.Component.kind == kind)
    rows = db.execute(q.order_by(models.Component.created_at.desc())).scalars().all()
    return [component_dict(c) for c in rows]


@router.get("/components/{ident}/impact", tags=["components"])
def component_impact(ident: str, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    """'What executions/outputs/certificates depend on this component?' — live view."""
    require_role(auth, allowed=READ_ROLES)
    comp = _get_component(db, tenant_uuid(auth), ident)
    return trust.component_impact(db, tenant_uuid(auth), comp)


@router.post("/components/{ident}/trust", tags=["components"])
def change_component_trust(
    ident: str, body: TrustChangeIn,
    request: Request, db: Session = Depends(get_db), auth: dict = Depends(get_auth),
):
    require_role(auth, allowed=MUTATE_ROLES)
    comp = _get_component(db, tenant_uuid(auth), ident)
    try:
        state = TrustState(body.state)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"invalid trust state {body.state}")

    if state == TrustState.COMPROMISED:
        result = trust.compromise_component(db, tenant_uuid(auth), comp, body.reason,
                                            actor=auth["key_name"])
        _audit(db, auth, request, "component.compromised", "component", str(comp.id),
               {"reason": body.reason, "affected": len(result["affected_executions"])})
        request.app.state.metrics.bump("components_compromised", 1)
        return result
    if state == TrustState.TRUSTED:
        result = trust.recover_component(db, tenant_uuid(auth), comp, body.reason,
                                         new_digest=body.new_digest, actor=auth["key_name"])
        _audit(db, auth, request, "component.recovered", "component", str(comp.id), {"reason": body.reason})
        return result
    comp.trust_state = state
    comp.state_reason = body.reason
    return {"component_id": str(comp.id), "state": state.value}


# --- integrity events / incidents ---------------------------------------------------------


@router.get("/integrity-events", tags=["integrity"])
def list_integrity_events(limit: int = 100, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    rows = db.execute(
        select(models.IntegrityEvent).where(models.IntegrityEvent.tenant_id == tenant_uuid(auth))
        .order_by(models.IntegrityEvent.created_at.desc()).limit(min(limit, 500))
    ).scalars().all()
    return [integrity_event_dict(e) for e in rows]


@router.get("/incidents", tags=["incidents"])
def list_incidents(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    rows = db.execute(
        select(models.Incident).where(models.Incident.tenant_id == tenant_uuid(auth))
        .order_by(models.Incident.created_at.desc())
    ).scalars().all()
    return [incident_dict(i) for i in rows]


@router.post("/incidents/{ident}/actions", tags=["incidents"])
def incident_action(
    ident: str, body: IncidentActionIn,
    request: Request, db: Session = Depends(get_db), auth: dict = Depends(get_auth),
):
    require_role(auth, allowed=MUTATE_ROLES)
    try:
        inc = db.get(models.Incident, uuid.UUID(ident))
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid incident id")
    if inc is None or inc.tenant_id != tenant_uuid(auth):
        raise HTTPException(status_code=404, detail="incident not found")

    if body.action == "contain":
        inc.status = IncidentStatus.CONTAINED
    elif body.action == "recover":
        inc.status = IncidentStatus.RECOVERING
        if body.new_digest and inc.root_component_id:
            comp = db.get(models.Component, inc.root_component_id)
            if comp is not None:
                comp.digest_expected = body.new_digest
    elif body.action == "resolve":
        inc.status = IncidentStatus.RESOLVED
        inc.resolved_at = models.utcnow()
    elif body.action == "rerun_note":
        inc.evidence = {**inc.evidence, "rerun_note": body.reason}
    _audit(db, auth, request, f"incident.{body.action}", "incident", str(inc.id), {"reason": body.reason})
    return incident_dict(inc)


# --- certificates ----------------------------------------------------------------------------


@router.get("/certificates", tags=["certificates"])
def list_certificates(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    rows = db.execute(
        select(models.Certificate).where(models.Certificate.tenant_id == tenant_uuid(auth))
        .order_by(models.Certificate.issued_at.desc())
    ).scalars().all()
    return [certificate_dict(c) for c in rows]


@router.get("/certificates/{serial}", tags=["certificates"])
def get_certificate(serial: str, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    cert = db.execute(
        select(models.Certificate).where(models.Certificate.tenant_id == tenant_uuid(auth),
                                         models.Certificate.serial == serial)
    ).scalar_one_or_none()
    if cert is None:
        raise HTTPException(status_code=404, detail="certificate not found")
    return certificate_dict(cert, include_statement=True)


@router.post("/certificates/{serial}/verify", tags=["certificates"])
def verify_certificate(serial: str, request: Request, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    public_pem = request.app.state.public_key_pem
    result = cert_service.verify_certificate(db, tenant_uuid(auth), serial, public_pem)
    return {
        "valid": result.valid, "reason": result.reason, "serial": serial,
        "status": result.certificate.status.value if result.certificate else None,
        "statement": result.certificate.statement if result.certificate else None,
    }


# --- policies ---------------------------------------------------------------------------------


@router.get("/policies", tags=["policies"])
def list_policies(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    rows = db.execute(
        select(models.Policy).where(models.Policy.tenant_id == tenant_uuid(auth))
    ).scalars().all()
    return [{"id": str(p.id), "name": p.name, "rules": p.rules,
             "effective_rules": effective_rules(p.rules), "is_default": p.is_default}
            for p in rows]


@router.put("/policies/{ident}", tags=["policies"])
def update_policy(ident: str, rules: dict, request: Request, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, minimum=Role.ADMIN)
    try:
        pol = db.get(models.Policy, uuid.UUID(ident))
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid policy id")
    if pol is None or pol.tenant_id != tenant_uuid(auth):
        raise HTTPException(status_code=404, detail="policy not found")
    pol.rules = rules
    _audit(db, auth, request, "policy.update", "policy", str(pol.id), {"rules": rules})
    return {"id": str(pol.id), "name": pol.name, "rules": pol.rules}


# --- auth management ---------------------------------------------------------------------------


@router.post("/auth/keys", tags=["auth"])
def create_api_key(body: ApiKeyCreateIn, request: Request, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, minimum=Role.ADMIN)
    raw = generate_api_key()
    row = models.ApiKey(
        tenant_id=auth["tenant_id"], name=body.name, key_hash=hash_api_key(raw),
        prefix=key_prefix(raw), role=Role(body.role),
    )
    db.add(row)
    db.flush()
    _audit(db, auth, request, "auth.key.create", "api_key", str(row.id), {"name": body.name, "role": body.role})
    return {"id": str(row.id), "key": raw, "prefix": row.prefix, "role": body.role,
            "note": "store this key now; it is not retrievable later"}


@router.post("/auth/verify", tags=["auth"])
def verify_key(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    return {"tenant_id": str(auth["tenant_id"]), "role": auth["role"].value, "key_name": auth["key_name"]}


# --- overview -------------------------------------------------------------------------------------


@router.get("/overview", tags=["overview"])
def overview(db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, allowed=READ_ROLES)
    tenant_id = tenant_uuid(auth)
    executions = db.execute(
        select(models.Execution).where(models.Execution.tenant_id == tenant_id)
    ).scalars().all()
    by_state: dict[str, int] = {}
    for e in executions:
        by_state[e.trust_state.value] = by_state.get(e.trust_state.value, 0) + 1
    components = db.execute(
        select(models.Component).where(models.Component.tenant_id == tenant_id)
    ).scalars().all()
    comp_by_state: dict[str, int] = {}
    for c in components:
        comp_by_state[c.trust_state.value] = comp_by_state.get(c.trust_state.value, 0) + 1
    incidents = db.execute(
        select(models.Incident).where(models.Incident.tenant_id == tenant_id,
                                      models.Incident.status != IncidentStatus.RESOLVED)
    ).scalars().all()
    ievents = db.execute(
        select(models.IntegrityEvent).where(models.IntegrityEvent.tenant_id == tenant_id)
        .order_by(models.IntegrityEvent.created_at.desc()).limit(10)
    ).scalars().all()
    return {
        "executions_total": len(executions),
        "executions_by_trust_state": by_state,
        "components_total": len(components),
        "components_by_trust_state": comp_by_state,
        "open_incidents": [incident_dict(i) for i in incidents],
        "recent_integrity_events": [integrity_event_dict(e) for e in ievents],
    }


# --- audit -----------------------------------------------------------------------------------------


@router.get("/audit", tags=["audit"])
def list_audit(limit: int = 100, db: Session = Depends(get_db), auth: dict = Depends(get_auth)):
    require_role(auth, minimum=Role.ADMIN)
    rows = db.execute(
        select(models.AuditLog).where(models.AuditLog.tenant_id == tenant_uuid(auth))
        .order_by(models.AuditLog.created_at.desc()).limit(min(limit, 500))
    ).scalars().all()
    return [{"id": str(a.id), "actor": a.actor, "action": a.action, "object_kind": a.object_kind,
             "object_id": a.object_id, "detail": a.detail, "created_at": _iso(a.created_at)}
            for a in rows]
