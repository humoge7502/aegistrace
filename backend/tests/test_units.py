"""Unit tests: fingerprinting, redaction, baseline comparison logic."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.security import looks_like_secret, redact_strings
from backend.app.domain import models
from backend.app.domain.enums import ExecutionStatus, TrustState
from backend.app.graph.service import compare_baseline, fingerprint_of, hash_content


def make_execution(steps: list[dict], meta: dict | None = None) -> models.Execution:
    ex = models.Execution(
        tenant_id=uuid.uuid4(), external_id="run-x", agent_ref="support-agent",
        status=ExecutionStatus.COMPLETED, trust_state=TrustState.UNKNOWN,
    )
    ex.steps = steps
    ex.meta = meta or {"prompt_hashes": {}}
    ex.fingerprint = fingerprint_of(steps)
    return ex


BASE = {
    "mode": "sequence",
    "steps": [
        {"seq": 1, "kind": "model", "target": "demo-model@1"},
        {"seq": 2, "kind": "retrieval", "target": "kb://policies"},
        {"seq": 3, "kind": "mcp", "target": "mcp://crm"},
    ],
    "allowed": {"mcp": ["mcp://crm"], "model": ["demo-model@1"]},
    "component_digests": {"mcp://crm": "sha256:" + "2" * 64},
    "prompt_hashes": {"system": "sha256:" + "a" * 64},
}


def test_fingerprint_is_order_sensitive_and_deterministic():
    a = [{"seq": 1, "kind": "model", "target": "m", "digest": None},
         {"seq": 2, "kind": "mcp", "target": "c", "digest": None}]
    b = [{"seq": 2, "kind": "mcp", "target": "c", "digest": None},
         {"seq": 1, "kind": "model", "target": "m", "digest": None}]
    assert fingerprint_of(a) == fingerprint_of(b)  # seq ordering normalizes
    c = [{"seq": 1, "kind": "mcp", "target": "c", "digest": None},
         {"seq": 2, "kind": "model", "target": "m", "digest": None}]
    assert fingerprint_of(a) != fingerprint_of(c)  # order change = different fingerprint


def test_digest_mismatch_detected():
    steps = [{"seq": 1, "kind": "mcp", "target": "mcp://crm", "digest": "sha256:" + "f" * 64}]
    ex = make_execution(steps)
    devs = compare_baseline(BASE, "sequence", ex)
    kinds = {d["kind"] for d in devs}
    assert "digest_mismatch" in kinds
    mismatch = next(d for d in devs if d["kind"] == "digest_mismatch")
    assert mismatch["severity"] == "critical"
    assert mismatch["observed"]["digest"] == "sha256:" + "f" * 64


def test_unexpected_component_and_path_deviation():
    steps = [
        {"seq": 1, "kind": "model", "target": "demo-model@1"},
        {"seq": 2, "kind": "mcp", "target": "mcp://evil-endpoint"},
        {"seq": 3, "kind": "mcp", "target": "mcp://crm"},
    ]
    ex = make_execution(steps)
    devs = compare_baseline(BASE, "sequence", ex)
    kinds = {d["kind"] for d in devs}
    assert "unexpected_component" in kinds
    assert "path_deviation" in kinds
    assert "missing_step" in kinds  # retrieval never happened


def test_clean_execution_has_no_deviations():
    steps = [
        {"seq": 1, "kind": "model", "target": "demo-model@1"},
        {"seq": 2, "kind": "retrieval", "target": "kb://policies"},
        {"seq": 3, "kind": "mcp", "target": "mcp://crm", "digest": "sha256:" + "2" * 64},
    ]
    ex = make_execution(steps, meta={"prompt_hashes": {"system": "sha256:" + "a" * 64}})
    assert compare_baseline(BASE, "sequence", ex) == []


def test_prompt_mismatch_detected():
    steps = [{"seq": 1, "kind": "model", "target": "demo-model@1"},
             {"seq": 2, "kind": "retrieval", "target": "kb://policies"},
             {"seq": 3, "kind": "mcp", "target": "mcp://crm", "digest": "sha256:" + "2" * 64}]
    ex = make_execution(steps, meta={"prompt_hashes": {"system": "sha256:" + "b" * 64}})
    devs = compare_baseline(BASE, "sequence", ex)
    assert any(d["kind"] == "prompt_mismatch" and d["severity"] == "critical" for d in devs)


def test_allowed_set_mode_permutes():
    steps = [
        {"seq": 1, "kind": "mcp", "target": "mcp://crm", "digest": "sha256:" + "2" * 64},
        {"seq": 2, "kind": "model", "target": "demo-model@1"},
        {"seq": 3, "kind": "retrieval", "target": "kb://policies"},
    ]
    ex = make_execution(steps, meta={"prompt_hashes": {"system": "sha256:" + "a" * 64}})
    devs = compare_baseline(BASE, "allowed_set", ex)
    assert devs == []  # same component set, different order: allowed


def test_allowed_set_mode_flags_missing_expected_step():
    steps = [{"seq": 1, "kind": "mcp", "target": "mcp://crm", "digest": "sha256:" + "2" * 64}]
    ex = make_execution(steps)
    devs = compare_baseline(BASE, "allowed_set", ex)
    assert any(d["kind"] == "missing_step" for d in devs)


def test_redaction():
    assert looks_like_secret("authorization: Bearer sk-abc123def456ghi789")
    assert looks_like_secret("api_key = sk-abcdefghijklmnopqrst")
    assert not looks_like_secret("the quarterly report looks good")
    cleaned = redact_strings({"note": "password: hunter2", "n": 3})
    assert cleaned["note"] == "[REDACTED]"
    assert cleaned["n"] == 3


def test_hash_content_stable():
    assert hash_content("hello") == hash_content("hello")
    assert hash_content("hello") != hash_content("hello ")
    assert hash_content({"a": 1, "b": 2}) == hash_content({"b": 2, "a": 1})
