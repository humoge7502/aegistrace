"""Cryptographic signing for AI Trust Certificates (ADR-004).

Ed25519 over canonical JSON (RFC 8785-flavored: sort_keys, compact separators,
UTF-8). The private key is generated on first startup and stored outside VCS.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def canonical_json(obj: object) -> bytes:
    """Deterministic JSON encoding used for signing and fingerprinting."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def generate_private_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


def load_or_create_key(path: Path) -> Ed25519PrivateKey:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        pem = path.read_bytes()
        key = serialization.load_pem_private_key(pem, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError(f"Signing key at {path} is not Ed25519")
        return key
    key = generate_private_key()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    path.write_bytes(pem)
    try:
        path.chmod(0o600)
    except OSError:  # pragma: no cover - Windows chmod is best-effort
        pass
    return key


def public_key_pem(key: Ed25519PrivateKey) -> bytes:
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def sign_bytes(key: Ed25519PrivateKey, payload: bytes) -> str:
    return base64.b64encode(key.sign(payload)).decode("ascii")


def verify_bytes(public_pem: bytes, payload: bytes, signature_b64: str) -> bool:
    try:
        pub = serialization.load_pem_public_key(public_pem)
        if not isinstance(pub, Ed25519PublicKey):
            return False
        pub.verify(base64.b64decode(signature_b64), payload)
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def verify_with_key(key: Ed25519PrivateKey, payload: bytes, signature_b64: str) -> bool:
    try:
        key.public_key().verify(base64.b64decode(signature_b64), payload)
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False
