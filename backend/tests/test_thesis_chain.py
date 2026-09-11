"""Integration tests — the core thesis chain end to end through ingestion:
normal -> TRUSTED + certificate; compromise -> detection -> UNTRUSTED ->
propagation -> invalidation -> recovery -> re-certification."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.collect.ingest import process_event
from backend.app.collect.schemas import EventIn
from backend.app.core.crypto import canonical_json, verify_with_key
from backend.app.domain import models
from backend.app.domain.enums import CertStatus, NodeKind, TrustState


def emit(client, auth_key, events):
    r = client.post("/api/v1/events/batch",
                    headers={"X-API-Key": auth_key}, json={"events": events})
    assert r.status_code == 200, r.text
    return r.json()


def run_normal(client, provisioned, demo_baseline, run_id="run-ok"):
    """Register baseline, then emit a clean execution; returns finished result."""
    r = client.post("/api/v1/baselines", headers={"X-API-Key": provisioned["admin_key"]},
                    json=demo_baseline)
    assert r.status_code == 200, r.text
    sys_dig = "sha256:" + "a" * 64
    out_digest = "sha256:" + "9" * 64
    return emit(client, provisioned["agent_key"], [
        {"kind": "execution.started", "execution_external_id": run_id,
         "payload": {"agent_ref": "support-agent", "agent_version": "1.0.0"}},
        {"kind": "prompt.pinned", "execution_external_id": run_id,
         "payload": {"role": "system", "hash": sys_dig}},
        {"kind": "step.ended", "execution_external_id": run_id,
         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1",
                     "digest": "sha256:" + "1" * 64}},
        {"kind": "step.ended", "execution_external_id": run_id,
         "payload": {"seq": 2, "kind": "retrieval", "target": "kb://policies",
                     "meta": {"documents": [{"id": "doc-1", "hash": "sha256:" + "d" * 64}]}}},
        {"kind": "step.ended", "execution_external_id": run_id,
         "payload": {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture",
                     "digest": "sha256:" + "2" * 64, "meta": {"tool": "lookup_customer"}}},
        {"kind": "step.ended", "execution_external_id": run_id,
         "payload": {"seq": 4, "kind": "tool", "target": "tool:send_email",
                     "digest": "sha256:" + "3" * 64}},
        {"kind": "output.produced", "execution_external_id": run_id,
         "payload": {"digest": out_digest}},
        {"kind": "execution.finished", "execution_external_id": run_id,
         "payload": {"execution_external_id": run_id, "status": "completed"}},
    ])


def test_clean_execution_is_trusted_and_certified(client, provisioned, demo_baseline):
    result = run_normal(client, provisioned, demo_baseline)["results"][-1]
    assert result["trust_state"] == "TRUSTED", result
    assert result["certificate"]

    r = client.get(f"/api/v1/executions/{result['execution_id']}/passport",
                   headers={"X-API-Key": provisioned["admin_key"]})
    assert r.status_code == 200
    passport = r.json()
    assert passport["trust"]["state"] == "TRUSTED"
    assert len(passport["components"]) == 4
    assert passport["certificate"]["status"] == "ACTIVE"
    assert passport["certificate"]["statement"]["predicateType"] == \
        "https://aegistrace.dev/attestations/execution-trust/v1"

    serial = passport["certificate"]["serial"]
    v = client.post(f"/api/v1/certificates/{serial}/verify",
                    headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert v["valid"] is True, v


def test_digest_compromise_detected_execution_untrusted(client, provisioned, demo_baseline):
    run_normal(client, provisioned, demo_baseline, run_id="run-good")
    # attacker swaps the MCP fixture; SDK observes the new digest
    result = emit(client, provisioned["agent_key"], [
        {"kind": "execution.started", "execution_external_id": "run-bad",
         "payload": {"agent_ref": "support-agent"}},
        {"kind": "step.ended", "execution_external_id": "run-bad",
         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1",
                     "digest": "sha256:" + "1" * 64}},
        {"kind": "step.ended", "execution_external_id": "run-bad",
         "payload": {"seq": 2, "kind": "retrieval", "target": "kb://policies"}},
        {"kind": "step.ended", "execution_external_id": "run-bad",
         "payload": {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture",
                     "digest": "sha256:" + "e" * 64, "meta": {"tool": "lookup_customer"}}},
        {"kind": "step.ended", "execution_external_id": "run-bad",
         "payload": {"seq": 4, "kind": "tool", "target": "tool:send_email",
                     "digest": "sha256:" + "3" * 64}},
        {"kind": "output.produced", "execution_external_id": "run-bad",
         "payload": {"digest": "sha256:" + "8" * 64}},
        {"kind": "execution.finished", "execution_external_id": "run-bad",
         "payload": {"execution_external_id": "run-bad", "status": "completed"}},
    ])["results"][-1]

    assert result["trust_state"] == "UNTRUSTED"
    assert result["certificate"] is None
    assert result["deviations"] >= 1

    r = client.get("/api/v1/integrity-events", headers={"X-API-Key": provisioned["admin_key"]})
    kinds = {e["kind"] for e in r.json()}
    assert "digest_mismatch" in kinds


def test_path_deviation_detected_despite_normal_output(client, provisioned, demo_baseline):
    """THE definitive experiment: output looks normal, execution path deviated."""
    r = client.post("/api/v1/baselines", headers={"X-API-Key": provisioned["admin_key"]},
                    json=demo_baseline)
    assert r.status_code == 200
    result = emit(client, provisioned["agent_key"], [
        {"kind": "execution.started", "execution_external_id": "run-dev",
         "payload": {"agent_ref": "support-agent"}},
        {"kind": "step.ended", "execution_external_id": "run-dev",
         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1",
                     "digest": "sha256:" + "1" * 64}},
        {"kind": "step.ended", "execution_external_id": "run-dev",
         "payload": {"seq": 2, "kind": "retrieval", "target": "kb://policies"}},
        {"kind": "step.ended", "execution_external_id": "run-dev",
         "payload": {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture",
                     "digest": "sha256:" + "2" * 64}},
        {"kind": "step.ended", "execution_external_id": "run-dev",
         "payload": {"seq": 4, "kind": "mcp", "target": "mcp://external-fixture",
                     "digest": "sha256:" + "f" * 64, "meta": {"tool": "exfiltrate"}}},
        {"kind": "step.ended", "execution_external_id": "run-dev",
         "payload": {"seq": 5, "kind": "tool", "target": "tool:send_email",
                     "digest": "sha256:" + "3" * 64}},
        {"kind": "output.produced", "execution_external_id": "run-dev",
         "payload": {"digest": "sha256:" + "7" * 64}},  # perfectly normal-looking output
        {"kind": "execution.finished", "execution_external_id": "run-dev",
         "payload": {"execution_external_id": "run-dev", "status": "completed"}},
    ])["results"][-1]
    assert result["trust_state"] == "UNTRUSTED"


def test_compromise_propagation_invalidates_history(client, provisioned, demo_baseline):
    """Component compromised AFTER the fact: historical outputs invalidated."""
    good = run_normal(client, provisioned, demo_baseline, run_id="run-hist")
    good_exec_id = good["results"][0]["execution_id"]

    certs = client.get("/api/v1/certificates", headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert len(certs) == 1 and certs[0]["status"] == "ACTIVE"
    active_serial = certs[0]["serial"]

    # find the MCP component and compromise it
    comps = client.get("/api/v1/components", headers={"X-API-Key": provisioned["admin_key"]}).json()
    mcp = next(c for c in comps if c["name"] == "mcp://crm-fixture")
    r = client.post(f"/api/v1/components/{mcp['id']}/trust",
                    headers={"X-API-Key": provisioned["admin_key"]},
                    json={"state": "COMPROMISED", "reason": "MCP fixture digest changed unexpectedly"})
    assert r.status_code == 200, r.text
    propagation = r.json()
    assert propagation["affected_executions"], propagation
    assert any(e["external_id"] == "run-hist" for e in propagation["affected_executions"])
    assert propagation["revoked_certificates"] == [active_serial]

    # historical output is now untrusted and quarantined
    passport = client.get(f"/api/v1/executions/{good_exec_id}/passport",
                          headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert passport["trust"]["state"] == "UNTRUSTED"
    assert passport["outputs"][0]["trust_state"] == "UNTRUSTED"
    assert passport["outputs"][0]["quarantined"] is True

    # certificate verification now fails with revocation
    v = client.post(f"/api/v1/certificates/{active_serial}/verify",
                    headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert v["valid"] is False
    assert "REVOKED" in v["reason"]

    # incident exists with evidence
    incidents = client.get("/api/v1/incidents", headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert any(i["root_component_id"] == mcp["id"] for i in incidents)
    inc = next(i for i in incidents if i["root_component_id"] == mcp["id"])
    assert inc["evidence"]["affected_outputs"]


def test_recovery_and_recertification(client, provisioned, demo_baseline):
    run_normal(client, provisioned, demo_baseline, run_id="run-rec")

    comps = client.get("/api/v1/components", headers={"X-API-Key": provisioned["admin_key"]}).json()
    mcp = next(c for c in comps if c["name"] == "mcp://crm-fixture")
    client.post(f"/api/v1/components/{mcp['id']}/trust", headers={"X-API-Key": provisioned["admin_key"]},
                json={"state": "COMPROMISED", "reason": "fixture tampered"})
    client.post(f"/api/v1/components/{mcp['id']}/trust", headers={"X-API-Key": provisioned["admin_key"]},
                json={"state": "TRUSTED", "reason": "fixture restored to trusted digest",
                      "new_digest": "sha256:" + "2" * 64})

    # re-run with the restored digest, marked as a rerun of the affected execution
    result = emit(client, provisioned["agent_key"], [
        {"kind": "execution.started", "execution_external_id": "run-rec-2",
         "payload": {"agent_ref": "support-agent", "rerun_of": "run-rec"}},
        {"kind": "step.ended", "execution_external_id": "run-rec-2",
         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1",
                     "digest": "sha256:" + "1" * 64}},
        {"kind": "step.ended", "execution_external_id": "run-rec-2",
         "payload": {"seq": 2, "kind": "retrieval", "target": "kb://policies"}},
        {"kind": "step.ended", "execution_external_id": "run-rec-2",
         "payload": {"seq": 3, "kind": "mcp", "target": "mcp://crm-fixture",
                     "digest": "sha256:" + "2" * 64}},
        {"kind": "step.ended", "execution_external_id": "run-rec-2",
         "payload": {"seq": 4, "kind": "tool", "target": "tool:send_email",
                     "digest": "sha256:" + "3" * 64}},
        {"kind": "output.produced", "execution_external_id": "run-rec-2",
         "payload": {"digest": "sha256:" + "6" * 64}},
        {"kind": "execution.finished", "execution_external_id": "run-rec-2",
         "payload": {"execution_external_id": "run-rec-2", "status": "completed"}},
    ])["results"][-1]
    assert result["trust_state"] == "RE-CERTIFIED", result
    assert result["certificate"]


def test_unknown_when_no_baseline(client, provisioned):
    result = emit(client, provisioned["agent_key"], [
        {"kind": "execution.started", "execution_external_id": "run-nobl",
         "payload": {"agent_ref": "unregistered-agent"}},
        {"kind": "step.ended", "execution_external_id": "run-nobl",
         "payload": {"seq": 1, "kind": "model", "target": "demo-model@1"}},
        {"kind": "output.produced", "execution_external_id": "run-nobl",
         "payload": {"digest": "sha256:" + "5" * 64}},
        {"kind": "execution.finished", "execution_external_id": "run-nobl",
         "payload": {"execution_external_id": "run-nobl", "status": "completed"}},
    ])["results"][-1]
    assert result["trust_state"] == "UNKNOWN"  # UNKNOWN != TRUSTED


def test_forged_certificate_rejected(client, provisioned, demo_baseline):
    run_normal(client, provisioned, demo_baseline, run_id="run-forge")
    certs = client.get("/api/v1/certificates", headers={"X-API-Key": provisioned["admin_key"]}).json()
    serial = certs[0]["serial"]

    # attacker tampers with the stored statement (simulating DB manipulation)
    factory = client.app.state.session_factory
    with factory() as db:
        from sqlalchemy import select
        cert = db.execute(select(models.Certificate).where(
            models.Certificate.serial == serial)).scalar_one()
        tampered = dict(cert.statement)
        tampered["predicate"] = {**tampered["predicate"], "trust_state": "TRUSTED-FORGED"}
        cert.statement = tampered
        db.commit()

    v = client.post(f"/api/v1/certificates/{serial}/verify",
                    headers={"X-API-Key": provisioned["admin_key"]}).json()
    assert v["valid"] is False
    assert "forged" in v["reason"].lower() or "signature" in v["reason"].lower()


def test_signature_verifies_against_stored_public_key(client, provisioned, demo_baseline):
    run_normal(client, provisioned, demo_baseline, run_id="run-sig")
    certs = client.get("/api/v1/certificates", headers={"X-API-Key": provisioned["admin_key"]}).json()
    cert = client.get(f"/api/v1/certificates/{certs[0]['serial']}",
                      headers={"X-API-Key": provisioned["admin_key"]}).json()
    from backend.app.core.crypto import verify_bytes
    assert verify_bytes(client.app.state.public_key_pem,
                        canonical_json(cert["statement"]), cert["signature"])
