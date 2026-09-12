"""SQLAlchemy ORM models — the AegisTrace relational causal graph.

Design notes (see docs/decisions/ADR-001..003):
- Nodes are typed references to existing entities (components / executions /
  outputs); edges live in a single `edges` table and are traversed with
  recursive CTEs, supported identically on SQLite and PostgreSQL.
- Every row is tenant-scoped. Tenancy is enforced in the query layer, not by
  relying on client-supplied ids.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.app.domain.enums import (
    CertStatus,
    ComponentKind,
    EdgeKind,
    EventKind,
    ExecutionStatus,
    FingerprintMode,
    IncidentStatus,
    IntegrityKind,
    NodeKind,
    PolicyAction,
    Role,
    Severity,
    TrustState,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> uuid.UUID:
    return uuid.uuid4()


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="tenant")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    prefix: Mapped[str] = mapped_column(String(12))
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped[Tenant] = relationship(back_populates="api_keys")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    # rules: {"on_critical": "untrust", "on_high": "degrade", "no_baseline": "unknown",
    #         "quarantine_outputs": true, "certify_trusted": true, "compromised_propagation": "all_history"}
    rules: Mapped[dict] = mapped_column(JSON, default=dict)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Component(Base):
    """A provenance entity participating in executions (model, tool, MCP server...)."""

    __tablename__ = "components"
    __table_args__ = (
        Index("ix_components_tenant_kind_name_version", "tenant_id", "kind", "name", "version", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    kind: Mapped[ComponentKind] = mapped_column(Enum(ComponentKind, native_enum=False))
    name: Mapped[str] = mapped_column(String(240))
    version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    digest_expected: Mapped[str | None] = mapped_column(String(80))
    digest_observed: Mapped[str | None] = mapped_column(String(80))
    trust_state: Mapped[TrustState] = mapped_column(Enum(TrustState, native_enum=False), default=TrustState.UNKNOWN)
    state_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Baseline(Base):
    """The expected execution contract for an agent (ADR-003)."""

    __tablename__ = "baselines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    agent_ref: Mapped[str] = mapped_column(String(240), index=True)
    agent_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mode: Mapped[FingerprintMode] = mapped_column(Enum(FingerprintMode, native_enum=False), default=FingerprintMode.SEQUENCE)
    # doc: {"steps": [{"seq":1,"kind":"model","target":"...","digest":"sha256:.."}],
    #       "allowed": {"tools": [...], "mcp": [...], "retrieval": [...], "model": [...]},
    #       "component_digests": {"mcp://crm": "sha256:..."},
    #       "prompt_hashes": {"system": "sha256:..."}}
    doc: Mapped[dict] = mapped_column(JSON, default=dict)
    policy_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("policies.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Execution(Base):
    __tablename__ = "executions"
    __table_args__ = (
        Index("ix_executions_tenant_external", "tenant_id", "external_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(80), index=True)  # SDK-provided run id
    baseline_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("baselines.id"), nullable=True)
    agent_ref: Mapped[str] = mapped_column(String(240), index=True)
    agent_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[ExecutionStatus] = mapped_column(Enum(ExecutionStatus, native_enum=False), default=ExecutionStatus.RUNNING)
    trust_state: Mapped[TrustState] = mapped_column(Enum(TrustState, native_enum=False), default=TrustState.UNKNOWN)
    # steps: [{"seq":1,"kind":"model","target":"...","digest":"sha256:..","ts":"..."}]
    steps: Mapped[list] = mapped_column(JSON, default=list)
    fingerprint: Mapped[str | None] = mapped_column(String(80))  # sha256 over canonical steps
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


class Output(Base):
    __tablename__ = "outputs"
    __table_args__ = (
        Index("ix_outputs_tenant_external", "tenant_id", "external_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    execution_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("executions.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(80), index=True)
    kind: Mapped[str] = mapped_column(String(60), default="text")
    digest: Mapped[str] = mapped_column(String(80))  # sha256 of output content
    trust_state: Mapped[TrustState] = mapped_column(Enum(TrustState, native_enum=False), default=TrustState.UNKNOWN)
    quarantined: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    execution: Mapped[Execution] = relationship()


class Edge(Base):
    """A causal edge. Directions: execution -step-> component, execution -produced-> output,
    component -depends_on-> component."""

    __tablename__ = "edges"
    __table_args__ = (
        Index("ix_edges_dst", "tenant_id", "dst_kind", "dst_id"),
        Index("ix_edges_src", "tenant_id", "src_kind", "src_id"),
        Index("ix_edges_exec", "tenant_id", "execution_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    src_kind: Mapped[NodeKind] = mapped_column(Enum(NodeKind, native_enum=False))
    src_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    dst_kind: Mapped[NodeKind] = mapped_column(Enum(NodeKind, native_enum=False))
    dst_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    kind: Mapped[EdgeKind] = mapped_column(Enum(EdgeKind, native_enum=False))
    execution_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("executions.id"), nullable=True)
    seq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected: Mapped[bool] = mapped_column(Boolean, default=True)  # False => deviation edge
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RawEvent(Base):
    """Append-only raw event log (source of truth for replay/audit)."""

    __tablename__ = "raw_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    execution_external_id: Mapped[str | None] = mapped_column(String(80), index=True)
    kind: Mapped[EventKind] = mapped_column(Enum(EventKind, native_enum=False))
    payload: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[str] = mapped_column(String(16), default="1")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IntegrityEvent(Base):
    """An expected-vs-observed deviation (or other integrity signal)."""

    __tablename__ = "integrity_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    execution_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("executions.id"), nullable=True, index=True)
    kind: Mapped[IntegrityKind] = mapped_column(Enum(IntegrityKind, native_enum=False))
    severity: Mapped[Severity] = mapped_column(Enum(Severity, native_enum=False))
    title: Mapped[str] = mapped_column(String(240))
    expected: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    observed: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TrustDecision(Base):
    """Explainable trust-state assignment for any subject (component/execution/output)."""

    __tablename__ = "trust_decisions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    subject_kind: Mapped[NodeKind] = mapped_column(Enum(NodeKind, native_enum=False), index=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    state: Mapped[TrustState] = mapped_column(Enum(TrustState, native_enum=False))
    reason: Mapped[str] = mapped_column(Text)
    # evidence: {"integrity_event_ids": [...], "chain": [{"from":..,"to":..,"kind":..}, ...],
    #            "policy": "...", "incident_id": "..."}
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    decided_by: Mapped[str] = mapped_column(String(60), default="trust-engine")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Certificate(Base):
    """Signed AI Trust Certificate (in-toto Statement v1 layout, ADR-004)."""

    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    execution_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("executions.id"), index=True)
    serial: Mapped[str] = mapped_column(String(40), unique=True, index=True)  # "ATC-<hex>"
    statement: Mapped[dict] = mapped_column(JSON)  # the in-toto statement (unsigned form)
    signature: Mapped[str] = mapped_column(String(200))  # base64 Ed25519 over canonical JSON
    alg: Mapped[str] = mapped_column(String(20), default="ed25519")
    key_id: Mapped[str] = mapped_column(String(80))
    status: Mapped[CertStatus] = mapped_column(Enum(CertStatus, native_enum=False), default=CertStatus.ACTIVE)
    revoked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(240))
    severity: Mapped[Severity] = mapped_column(Enum(Severity, native_enum=False), default=Severity.HIGH)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus, native_enum=False), default=IncidentStatus.OPEN)
    root_component_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("components.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class QuarantineAction(Base):
    __tablename__ = "quarantine_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), index=True)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("incidents.id"), nullable=True)
    target_kind: Mapped[NodeKind] = mapped_column(Enum(NodeKind, native_enum=False))
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    action: Mapped[PolicyAction] = mapped_column(Enum(PolicyAction, native_enum=False))
    result: Mapped[str] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_id)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(120))  # key name / "system"
    action: Mapped[str] = mapped_column(String(120))
    object_kind: Mapped[str] = mapped_column(String(60))
    object_id: Mapped[str] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MetricSample(Base):
    """Lightweight local metrics store (single-instance; OTel exporter is optional)."""

    __tablename__ = "metric_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
