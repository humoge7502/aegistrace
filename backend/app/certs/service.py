"""AI Trust Certificates — issue, verify, revoke (ADR-004).

Payload layout (in-toto Statement v1):
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{"name": "execution:<external_id>", "digest": {"sha256": "<fingerprint>"}}],
  "predicateType": "https://aegistrace.dev/attestations/execution-trust/v1",
  "predicate": {...trust evidence...}
}
Signed with Ed25519 over canonical JSON. Verification = signature + revocation
status + subject digest match against the current execution fingerprint.
"""

from __future__ import annotations

import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.crypto import canonical_json, sign_bytes, verify_bytes
from backend.app.core.security import redact_strings
from backend.app.domain import models
from backend.app.domain.enums import CertStatus, TrustState

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://aegistrace.dev/attestations/execution-trust/v1"


class VerificationResult:
    def __init__(self, valid: bool, reason: str, certificate: models.Certificate | None) -> None:
        self.valid = valid
        self.reason = reason
        self.certificate = certificate


def build_statement(
    execution: models.Execution,
    trust_state: TrustState,
    reason: str,
    evidence: dict,
    tenant_name: str,
) -> dict:
    steps = sorted(execution.steps, key=lambda s: s.get("seq", 0))
    components = [
        {"kind": s.get("kind"), "target": s.get("target"), "digest": s.get("digest")}
        for s in steps
    ]
    return {
        "_type": STATEMENT_TYPE,
        "subject": [{"name": f"execution:{execution.external_id}",
                     "digest": {"sha256": (execution.fingerprint or "").removeprefix("sha256:")}}],
        "predicateType": PREDICATE_TYPE,
        "predicate": redact_strings({
            "tenant": tenant_name,
            "agent_ref": execution.agent_ref,
            "agent_version": execution.agent_version,
            "trust_state": trust_state.value,
            "decision_reason": reason,
            "status": execution.status.value,
            "components": components,
            "fingerprint": execution.fingerprint,
            "evidence": evidence,
            "issued_at": models.utcnow().isoformat(),
        }),
    }


def issue_certificate(
    session: Session,
    tenant_id: uuid.UUID,
    execution: models.Execution,
    trust_state: TrustState,
    reason: str,
    evidence: dict,
    signing_key,
    key_id: str,
    tenant_name: str,
) -> models.Certificate:
    statement = build_statement(execution, trust_state, reason, evidence, tenant_name)
    signature = sign_bytes(signing_key, canonical_json(statement))
    cert = models.Certificate(
        tenant_id=tenant_id,
        execution_id=execution.id,
        serial="ATC-" + secrets.token_hex(8),
        statement=statement,
        signature=signature,
        alg="ed25519",
        key_id=key_id,
        status=CertStatus.ACTIVE,
    )
    session.add(cert)
    session.flush()
    return cert


def verify_certificate(session: Session, tenant_id: uuid.UUID, serial: str,
                       public_pem: bytes) -> VerificationResult:
    cert = session.execute(
        select(models.Certificate).where(
            models.Certificate.tenant_id == tenant_id, models.Certificate.serial == serial)
    ).scalar_one_or_none()
    if cert is None:
        return VerificationResult(False, "certificate not found", None)

    if not verify_bytes(public_pem, canonical_json(cert.statement), cert.signature):
        return VerificationResult(False, "signature verification FAILED (forged or tampered)", cert)

    if cert.status == CertStatus.REVOKED:
        return VerificationResult(False, f"certificate REVOKED: {cert.revoked_reason}", cert)

    execution = session.get(models.Execution, cert.execution_id)
    if execution is None:
        return VerificationResult(False, "referenced execution missing", cert)
    if execution.fingerprint != cert.statement["subject"][0]["digest"].get("sha256") and \
            ("sha256:" + cert.statement["subject"][0]["digest"].get("sha256", "")) != execution.fingerprint:
        return VerificationResult(False, "subject digest no longer matches execution fingerprint", cert)

    return VerificationResult(True, "signature valid, certificate active, subject matches", cert)
