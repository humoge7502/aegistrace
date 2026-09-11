"""Security tests: authentication, RBAC, tenancy isolation, rate limiting,
input validation, security headers, audit logging."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_missing_key_401(client):
    r = client.get("/api/v1/executions")
    assert r.status_code == 401


def test_invalid_key_401(client):
    r = client.get("/api/v1/executions", headers={"X-API-Key": "at_totally_fake"})
    assert r.status_code == 401


def test_agent_role_cannot_read(client, provisioned):
    r = client.get("/api/v1/executions", headers={"X-API-Key": provisioned["agent_key"]})
    assert r.status_code == 403


def test_viewer_cannot_ingest(client, provisioned):
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["viewer_key"]},
                    json={"events": [{"kind": "execution.started",
                                      "execution_external_id": "x", "payload": {}}]})
    assert r.status_code == 403


def test_viewer_cannot_compromise_component(client, provisioned):
    r = client.post("/api/v1/components/00000000-0000-0000-0000-000000000000/trust",
                    headers={"X-API-Key": provisioned["viewer_key"]},
                    json={"state": "COMPROMISED", "reason": "x"})
    assert r.status_code == 403


def test_tenant_isolation(client, provisioned, demo_baseline):
    """Tenant B must not see or affect tenant A's data."""
    client.post("/api/v1/baselines", headers={"X-API-Key": provisioned["admin_key"]},
                json=demo_baseline)
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                    json={"events": [
                        {"kind": "execution.started", "execution_external_id": "run-iso",
                         "payload": {"agent_ref": "support-agent"}},
                        {"kind": "execution.finished", "execution_external_id": "run-iso",
                         "payload": {"execution_external_id": "run-iso", "status": "completed"}},
                    ]})
    assert r.status_code == 200

    # second tenant
    from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
    from backend.app.domain import models
    factory = client.app.state.session_factory
    other_key = generate_api_key()
    with factory() as db:
        t2 = models.Tenant(name=f"t-{generate_api_key()[:8]}")
        db.add(t2)
        db.flush()
        db.add(models.ApiKey(tenant_id=t2.id, name="admin2", key_hash=hash_api_key(other_key),
                             prefix=key_prefix(other_key), role=models.Role.ADMIN))
        db.commit()

    assert client.get("/api/v1/executions", headers={"X-API-Key": other_key}).json() == []
    r = client.get("/api/v1/executions/run-iso", headers={"X-API-Key": other_key})
    assert r.status_code == 404
    r = client.get("/api/v1/executions/run-iso/passport", headers={"X-API-Key": other_key})
    assert r.status_code == 404


def test_rate_limiting(client, test_env, monkeypatch):
    monkeypatch.setenv("AEGISTRACE_RATE_LIMIT_PER_MINUTE", "3")
    from fastapi.testclient import TestClient

    from backend.app.core.config import get_settings
    from backend.app.main import create_app
    get_settings.cache_clear()
    try:
        app = create_app()
        with TestClient(app) as c:
            from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
            from backend.app.domain import models
            key = generate_api_key()
            with app.state.session_factory() as db:
                t = models.Tenant(name="rl-tenant")
                db.add(t)
                db.flush()
                db.add(models.ApiKey(tenant_id=t.id, name="rl", key_hash=hash_api_key(key),
                                     prefix=key_prefix(key), role=models.Role.ADMIN))
                db.commit()
            codes = [c.get("/api/v1/executions", headers={"X-API-Key": key}).status_code
                     for _ in range(6)]
            assert codes[:3] == [200, 200, 200]
            assert 429 in codes[3:]
    finally:
        get_settings.cache_clear()


def test_security_headers(client):
    r = client.get("/healthz")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Cache-Control"] == "no-store"


def test_invalid_event_rejected_with_422(client, provisioned):
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                    json={"events": [{"kind": "not-a-kind", "payload": {}}]})
    assert r.status_code == 422


def test_step_without_execution_422(client, provisioned):
    r = client.post("/api/v1/events/batch", headers={"X-API-Key": provisioned["agent_key"]},
                    json={"events": [{"kind": "step.ended",
                                      "execution_external_id": "ghost",
                                      "payload": {"seq": 1, "kind": "model", "target": "m"}}]})
    assert r.status_code == 422
    assert "unknown execution" in r.json()["detail"]


def test_audit_log_written_for_mutations(client, provisioned):
    client.post("/api/v1/baselines", headers={"X-API-Key": provisioned["admin_key"]},
                json={"agent_ref": "a1", "mode": "sequence", "steps": []})
    audit = client.get("/api/v1/audit", headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert any(a["action"] == "baseline.create" for a in audit)


def test_audit_requires_admin(client, provisioned):
    r = client.get("/api/v1/audit", headers={"X-API-Key": provisioned["operator_key"]
                                             if "operator_key" in provisioned else provisioned["viewer_key"]})
    assert r.status_code == 403
