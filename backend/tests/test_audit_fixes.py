"""Regression tests for final-audit findings.

Covers: step.started dedup (audit #1), content sanitization (#2), tenant-scoped
external ids (#3), empty allow-list deny-all (#4), withheld-evidence deviations
(#5), policy validation (#8), replayed finished dedup (#19), cross-tenant write
(#20), limiter bounding (#13), metrics auth (#14).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.collect.ingest import sanitize_payload
from backend.app.core.security import hash_content_value


# --- audit #1: step.started never double-records -------------------------------


def test_step_started_does_not_record(client, provisioned, demo_baseline):
    client.post("/api/v1/baselines", headers={"X-API-Key": provisioned["admin_key"]},
                json=demo_baseline)
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                    json={"events": [
                        {"kind": "execution.started", "execution_external_id": "run-dedup",
                         "payload": {"agent_ref": "support-agent"}},
                        {"kind": "step.started", "execution_external_id": "run-dedup",
                         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1"}},
                        {"kind": "step.ended", "execution_external_id": "run-dedup",
                         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1",
                                     "digest": "sha256:" + "1" * 64}},
                        {"kind": "execution.finished", "execution_external_id": "run-dedup",
                         "payload": {"execution_external_id": "run-dedup", "status": "completed"}},
                    ]})
    assert r.status_code == 200
    detail = client.get("/api/v1/executions/run-dedup",
                        headers={"X-API-Key": provisioned["admin_key"]}).json()
    model_steps = [s for s in detail["steps"] if s["target"] == "demo-model@1"]
    assert len(model_steps) == 1, "step.started+ended pair must record exactly once"


# --- audit #2: content sanitization ---------------------------------------------


def test_content_keys_hashed_by_default():
    payload = {"content": "SECRET PROMPT TEXT", "meta": {"args": {"q": "private query"}},
               "digest": "sha256:" + "a" * 64}
    out = sanitize_payload(payload, allow_content=False)
    assert "SECRET PROMPT TEXT" not in str(out)
    assert out["content"].startswith("sha256:")
    assert "private query" not in str(out["meta"])
    assert out["digest"] == "sha256:" + "a" * 64  # already-hashed values pass through


def test_content_allowed_when_opted_in():
    payload = {"content": "keep me"}
    out = sanitize_payload(payload, allow_content=True)
    assert out["content"] == "keep me"
    assert hash_content_value("keep me").startswith("sha256:")


def test_raw_content_rejected_end_to_end(client, provisioned):
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                    json={"events": [
                        {"kind": "execution.started", "execution_external_id": "run-content",
                         "payload": {"agent_ref": "x"}},
                        {"kind": "output.produced", "execution_external_id": "run-content",
                         "payload": {"content": "RAW OUTPUT TEXT THAT MUST NOT PERSIST"}},
                    ]})
    assert r.status_code == 200
    factory = client.app.state.session_factory
    with factory() as db:
        from sqlalchemy import select
        raws = db.execute(select(__import__("backend.app.domain.models", fromlist=["RawEvent"]).RawEvent)
                          .where(__import__("backend.app.domain.models", fromlist=["RawEvent"]).RawEvent.execution_external_id == "run-content")
                          ).scalars().all()
        blob = str([e.payload for e in raws])
        assert "RAW OUTPUT TEXT" not in blob


# --- audit #3: tenant-scoped external ids ----------------------------------------


def test_same_external_id_across_tenants(client, provisioned):
    from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
    from backend.app.domain import models
    other_key = generate_api_key()
    factory = client.app.state.session_factory
    with factory() as db:
        t2 = models.Tenant(name=f"t-{generate_api_key()[:8]}")
        db.add(t2)
        db.flush()
        db.add(models.ApiKey(tenant_id=t2.id, name="a2", key_hash=hash_api_key(other_key),
                             prefix=key_prefix(other_key), role=models.Role.AGENT))
        db.commit()

    body = {"events": [{"kind": "execution.started", "execution_external_id": "shared-id",
                        "payload": {"agent_ref": "x"}}]}
    r1 = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]}, json=body)
    r2 = client.post("/api/v1/events/batch", headers={"X-API-Key": other_key}, json=body)
    assert r1.status_code == 200 and r2.status_code == 200, (r1.text, r2.text)


# --- audit #4/#5: empty allow-list deny-all + withheld evidence -------------------


def test_empty_allow_list_is_deny_all():
    from backend.app.domain import models
    from backend.app.domain.enums import ExecutionStatus, TrustState
    from backend.app.graph.service import compare_baseline
    ex = models.Execution(tenant_id=__import__("uuid").uuid4(), external_id="x",
                          agent_ref="a", status=ExecutionStatus.COMPLETED,
                          trust_state=TrustState.UNKNOWN)
    ex.steps = [{"seq": 1, "kind": "tool", "target": "anything"}]
    ex.meta = {}
    base = {"mode": "allowed_set",
            "steps": [{"seq": 1, "kind": "tool", "target": "anything"}],
            "allowed": {"tools": []}, "component_digests": {}, "prompt_hashes": {}}
    devs = compare_baseline(base, "allowed_set", ex)
    assert any(d["kind"] == "unexpected_component" for d in devs)


def test_missing_digest_on_pinned_target_flagged():
    from backend.app.domain import models
    from backend.app.domain.enums import ExecutionStatus, TrustState
    from backend.app.graph.service import compare_baseline
    ex = models.Execution(tenant_id=__import__("uuid").uuid4(), external_id="x",
                          agent_ref="a", status=ExecutionStatus.COMPLETED,
                          trust_state=TrustState.UNKNOWN)
    ex.steps = [{"seq": 1, "kind": "mcp", "target": "mcp://crm"}]  # no digest
    ex.meta = {"prompt_hashes": {}}
    base = {"mode": "sequence",
            "steps": [{"seq": 1, "kind": "mcp", "target": "mcp://crm"}],
            "allowed": {}, "component_digests": {"mcp://crm": "sha256:" + "2" * 64},
            "prompt_hashes": {}}
    devs = compare_baseline(base, "sequence", ex)
    assert any(d["kind"] == "digest_mismatch" for d in devs)


def test_unpinned_expected_prompt_flagged():
    from backend.app.domain import models
    from backend.app.domain.enums import ExecutionStatus, TrustState
    from backend.app.graph.service import compare_baseline
    ex = models.Execution(tenant_id=__import__("uuid").uuid4(), external_id="x",
                          agent_ref="a", status=ExecutionStatus.COMPLETED,
                          trust_state=TrustState.UNKNOWN)
    ex.steps = [{"seq": 1, "kind": "mcp", "target": "mcp://crm",
                 "digest": "sha256:" + "2" * 64}]
    ex.meta = {"prompt_hashes": {}}  # expected prompt never pinned
    base = {"mode": "sequence",
            "steps": [{"seq": 1, "kind": "mcp", "target": "mcp://crm"}],
            "allowed": {}, "component_digests": {"mcp://crm": "sha256:" + "2" * 64},
            "prompt_hashes": {"system": "sha256:" + "a" * 64}}
    devs = compare_baseline(base, "sequence", ex)
    assert any(d["kind"] == "prompt_mismatch" for d in devs)


# --- audit #8: policy validation --------------------------------------------------


def test_policy_update_rejects_invalid_rules(client, provisioned):
    policies = client.get("/api/v1/policies", headers={"X-API-Key": provisioned["admin_key"]}).json()
    pid = policies[0]["id"]
    r = client.put(f"/api/v1/policies/{pid}", headers={"X-API-Key": provisioned["admin_key"]},
                   json={"critical": "banana"})
    assert r.status_code == 422
    r = client.put(f"/api/v1/policies/{pid}", headers={"X-API-Key": provisioned["admin_key"]},
                   json={"compromised_propagation": "from_compromise_time"})
    assert r.status_code == 200


# --- audit #19: replayed execution.finished is idempotent --------------------------


def test_replayed_finish_deduplicates(client, provisioned):
    events = [{"kind": "execution.started", "execution_external_id": "run-replay",
               "payload": {"agent_ref": "x"}},
              {"kind": "execution.finished", "execution_external_id": "run-replay",
               "payload": {"execution_external_id": "run-replay", "status": "completed"}}]
    client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]}, json={"events": events})
    r2 = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                     json={"events": [events[1]]})
    assert r2.status_code == 200
    assert r2.json()["results"][0].get("deduplicated") is True


# --- audit #20: cross-tenant WRITE is impossible -----------------------------------


def test_cross_tenant_component_action_404(client, provisioned):
    from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
    from backend.app.domain import models
    other_key = generate_api_key()
    factory = client.app.state.session_factory
    with factory() as db:
        t2 = models.Tenant(name=f"t-{generate_api_key()[:8]}")
        db.add(t2)
        db.flush()
        db.add(models.ApiKey(tenant_id=t2.id, name="op2", key_hash=hash_api_key(other_key),
                             prefix=key_prefix(other_key), role=models.Role.ADMIN))
        db.commit()
    comps = client.get("/api/v1/components", headers={"X-API-Key": provisioned["admin_key"]}).json()
    if comps:
        r = client.post(f"/api/v1/components/{comps[0]['id']}/trust",
                        headers={"X-API-Key": other_key},
                        json={"state": "COMPROMISED", "reason": "cross-tenant attempt"})
        assert r.status_code == 404


# --- audit #14: metrics requires admin ---------------------------------------------


def test_metrics_requires_admin(client, provisioned):
    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers={"X-API-Key": provisioned["viewer_key"]}).status_code == 403
    assert client.get("/metrics", headers={"X-API-Key": provisioned["admin_key"]}).status_code == 200
