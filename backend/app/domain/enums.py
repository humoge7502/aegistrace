"""Core domain enumerations for AegisTrace."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    AGENT = "agent"  # ingestion-only keys used by the SDK/collectors
    VIEWER = "viewer"


class ComponentKind(StrEnum):
    MODEL = "model"
    MODEL_ARTIFACT = "model_artifact"
    DATASET = "dataset"
    DATASET_VERSION = "dataset_version"
    PROMPT = "prompt"
    SYSTEM_PROMPT = "system_prompt"
    EMBEDDING_MODEL = "embedding_model"
    VECTOR_INDEX = "vector_index"
    DOCUMENT = "document"
    CORPUS = "corpus"
    AGENT = "agent"
    TOOL = "tool"
    MCP_SERVER = "mcp_server"
    PACKAGE = "package"
    DEPENDENCY = "dependency"
    CONTAINER = "container"
    IMAGE = "image"
    RUNTIME = "runtime"
    API = "api"
    EXTERNAL_SERVICE = "external_service"


class StepKind(StrEnum):
    MODEL = "model"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    MCP = "mcp"
    API = "api"
    EMBEDDING = "embedding"
    RUNTIME = "runtime"
    PACKAGE = "package"
    CUSTOM = "custom"


class EventKind(StrEnum):
    EXECUTION_STARTED = "execution.started"
    EXECUTION_FINISHED = "execution.finished"
    STEP_STARTED = "step.started"
    STEP_ENDED = "step.ended"
    COMPONENT_OBSERVED = "component.observed"
    OUTPUT_PRODUCED = "output.produced"
    PROMPT_PINNED = "prompt.pinned"


class TrustState(StrEnum):
    TRUSTED = "TRUSTED"
    UNTRUSTED = "UNTRUSTED"
    UNKNOWN = "UNKNOWN"
    DEGRADED = "DEGRADED"
    COMPROMISED = "COMPROMISED"
    QUARANTINED = "QUARANTINED"
    RECOVERING = "RECOVERING"
    RE_CERTIFIED = "RE-CERTIFIED"


class IntegrityKind(StrEnum):
    DIGEST_MISMATCH = "digest_mismatch"
    UNEXPECTED_COMPONENT = "unexpected_component"
    PATH_DEVIATION = "path_deviation"
    MISSING_STEP = "missing_step"
    STALE_EVIDENCE = "stale_evidence"
    FORGED_ATTESTATION = "forged_attestation"
    MISSING_PROVENANCE = "missing_provenance"
    PROMPT_MISMATCH = "prompt_mismatch"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CertStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    CONTAINED = "CONTAINED"
    RECOVERING = "RECOVERING"
    RESOLVED = "RESOLVED"


class PolicyAction(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    QUARANTINE = "quarantine"
    INVALIDATE = "invalidate"
    REQUIRE_APPROVAL = "require_approval"
    ROLLBACK = "rollback"
    RERUN = "rerun"
    CERTIFY = "certify"


class EdgeKind(StrEnum):
    STEP = "step"  # execution -> component (component participated in execution)
    PRODUCED = "produced"  # execution -> output
    DEPENDS_ON = "depends_on"  # component -> component


class NodeKind(StrEnum):
    COMPONENT = "component"
    EXECUTION = "execution"
    OUTPUT = "output"


class FingerprintMode(StrEnum):
    SEQUENCE = "sequence"  # exact ordered steps expected
    ALLOWED_SET = "allowed_set"  # steps must be within allowed sets, any order
    POLICY_ONLY = "policy_only"  # digest checks only; path unconstrained
