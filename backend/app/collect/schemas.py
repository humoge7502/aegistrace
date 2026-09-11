"""Event envelope schemas for collector ingestion.

The SDK emits a small, stable event vocabulary (see domain.enums.EventKind).
All events carry: kind, execution_external_id (except where noted), ts, payload.
Raw content is hashed by the SDK; the backend re-sanitizes as defense in depth.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    kind: str = Field(pattern=r"^(execution\.started|execution\.finished|step\.started|step\.ended|component\.observed|output\.produced|prompt\.pinned)$")
    execution_external_id: str | None = None
    ts: str | None = None  # ISO-8601; server time used if absent
    payload: dict = Field(default_factory=dict)


class EventBatchIn(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=1000)


class BaselineStepIn(BaseModel):
    seq: int
    kind: str
    target: str
    digest: str | None = None


class BaselineIn(BaseModel):
    agent_ref: str
    agent_version: str | None = None
    mode: str = "sequence"  # sequence | allowed_set | policy_only
    steps: list[BaselineStepIn] = Field(default_factory=list)
    allowed: dict[str, list[str]] = Field(default_factory=dict)
    component_digests: dict[str, str] = Field(default_factory=dict)
    prompt_hashes: dict[str, str] = Field(default_factory=dict)
    policy_id: str | None = None


class TrustChangeIn(BaseModel):
    state: str  # TrustState value, e.g. COMPROMISED / TRUSTED
    reason: str
    new_digest: str | None = None


class IncidentActionIn(BaseModel):
    action: str = Field(pattern=r"^(contain|recover|resolve|rerun_note)$")
    reason: str = ""
    new_digest: str | None = None
