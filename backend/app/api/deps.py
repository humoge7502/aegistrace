"""FastAPI dependencies: DB session, API-key auth, RBAC, rate limiting."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import hash_api_key
from backend.app.domain.enums import Role

ROLE_ORDER = {Role.VIEWER: 0, Role.AGENT: 1, Role.OPERATOR: 2, Role.ADMIN: 3}


def get_db(request: Request):
    factory = request.app.state.session_factory
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_auth(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """Authenticate via X-API-Key (or Bearer). Enforces role + rate limits."""
    key_raw = x_api_key
    if key_raw is None and authorization and authorization.lower().startswith("bearer "):
        key_raw = authorization.split(" ", 1)[1]
    if not key_raw:
        raise HTTPException(status_code=401, detail="missing API key")

    limiter = request.app.state.rate_limiter
    if not limiter.allow(hash_api_key(key_raw)[:16]):
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    row = db.execute(
        select(request.app.state.models.ApiKey).where(
            request.app.state.models.ApiKey.key_hash == hash_api_key(key_raw))
    ).scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        raise HTTPException(status_code=401, detail="invalid or revoked API key")

    return {"tenant_id": row.tenant_id, "role": Role(row.role), "key_name": row.name, "key_id": row.id}


def require_role(auth: dict, allowed: set[Role] | None = None, minimum: Role | None = None) -> None:
    if minimum is not None:
        if ROLE_ORDER[auth["role"]] < ROLE_ORDER[minimum]:
            raise HTTPException(status_code=403, detail=f"requires role {minimum.value} or above")
        return
    if allowed is not None and auth["role"] not in allowed:
        raise HTTPException(status_code=403, detail="insufficient role")


def tenant_uuid(auth: dict) -> uuid.UUID:
    return auth["tenant_id"]
