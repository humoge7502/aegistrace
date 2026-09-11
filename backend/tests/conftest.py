"""Pytest configuration: isolated app instance per test (own SQLite DB + signing key)."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture()
def test_env(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("AEGISTRACE_DATABASE_URL", f"sqlite:///{db.as_posix()}")
    monkeypatch.setenv("AEGISTRACE_SIGNING_KEY_PATH", str(tmp_path / "signing.pem"))
    from backend.app.core.config import get_settings
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()


@pytest.fixture()
def client(test_env):
    from fastapi.testclient import TestClient

    from backend.app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def provisioned(client):
    """A fresh tenant with admin + agent + viewer keys."""
    from backend.app.core.security import generate_api_key, hash_api_key, key_prefix
    from backend.app.domain import models

    factory = client.app.state.session_factory
    admin_key, agent_key, viewer_key = generate_api_key(), generate_api_key(), generate_api_key()
    with factory() as db:
        tenant = models.Tenant(name=f"t-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        db.flush()
        db.add(models.ApiKey(tenant_id=tenant.id, name="admin", key_hash=hash_api_key(admin_key),
                             prefix=key_prefix(admin_key), role=models.Role.ADMIN))
        db.add(models.ApiKey(tenant_id=tenant.id, name="agent", key_hash=hash_api_key(agent_key),
                             prefix=key_prefix(agent_key), role=models.Role.AGENT))
        db.add(models.ApiKey(tenant_id=tenant.id, name="viewer", key_hash=hash_api_key(viewer_key),
                             prefix=key_prefix(viewer_key), role=models.Role.VIEWER))
        db.add(models.Policy(tenant_id=tenant.id, name="default", rules={}, is_default=True))
        db.commit()
        client.app.state.tenant_names[tenant.id] = tenant.name
        tid = str(tenant.id)
    return {"tenant_id": tid, "admin_key": admin_key, "agent_key": agent_key, "viewer_key": viewer_key}


@pytest.fixture()
def demo_baseline():
    """Standard expected contract for the demo agent."""
    return {
        "agent_ref": "support-agent",
        "agent_version": "1.0.0",
        "mode": "sequence",
        "steps": [
            {"seq": 1, "kind": "model", "target": "demo-model@1"},
            {"seq": 2, "kind": "retrieval", "target": "kb://policies"},
            {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture"},
            {"seq": 4, "kind": "tool", "target": "tool:send_email"},
        ],
        "allowed": {
            "tools": ["tool:send_email"],
            "mcp": ["mcp://crm-fixture"],
            "retrieval": ["kb://policies"],
            "model": ["demo-model@1"],
        },
        "component_digests": {
            "demo-model@1": "sha256:" + "1" * 64,
            "mcp://crm-fixture": "sha256:" + "2" * 64,
            "tool:send_email": "sha256:" + "3" * 64,
        },
        "prompt_hashes": {"system": "sha256:" + "a" * 64},
    }
