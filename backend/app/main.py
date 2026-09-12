"""AegisTrace FastAPI application factory."""

from __future__ import annotations

import contextlib
import logging
import uuid
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select, text

from backend.app.api.v1 import router as v1_router
from backend.app.core.config import get_settings
from backend.app.core.crypto import load_or_create_key, public_key_pem
from backend.app.core.db import make_engine, make_session_factory
from backend.app.core.metrics import Metrics
from backend.app.core.security import RateLimiter, generate_api_key, hash_api_key, key_prefix
from backend.app.domain import models

logger = logging.getLogger("aegistrace")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.removeprefix("sqlite:///")
        import os
        os.makedirs(db_path.rsplit("/", 1)[0], exist_ok=True)

    engine = make_engine(settings.database_url)
    models.Base.metadata.create_all(engine)
    factory = make_session_factory(engine)

    # bootstrap: default tenant + admin key + default policy
    bootstrap_key: str | None = None
    tenant_names: dict[uuid.UUID, str] = {}
    with factory() as db:
        tenant = db.execute(select(models.Tenant).where(models.Tenant.name == "local")).scalar_one_or_none()
        if tenant is None:
            tenant = models.Tenant(name="local")
            db.add(tenant)
            db.flush()
            logger.warning("=" * 60)
            if settings.bootstrap_key:
                bootstrap_key = settings.bootstrap_key
            else:
                bootstrap_key = generate_api_key()
            db.add(models.ApiKey(
                tenant_id=tenant.id, name="bootstrap-admin",
                key_hash=hash_api_key(bootstrap_key), prefix=key_prefix(bootstrap_key),
                role=models.Role.ADMIN,
            ))
            db.add(models.Policy(tenant_id=tenant.id, name="default", rules={}, is_default=True))
            db.commit()
            logger.warning("BOOTSTRAP ADMIN API KEY (store it now; shown once): %s", bootstrap_key)
            logger.warning("=" * 60)
        tenant_names[tenant.id] = tenant.name

    app.state.engine = engine
    app.state.session_factory = factory
    app.state.settings = settings
    app.state.models = models
    app.state.metrics = Metrics()
    app.state.rate_limiter = RateLimiter(settings.rate_limit_per_minute)
    app.state.signing_key = load_or_create_key(settings.signing_key_path)
    app.state.public_key_pem = public_key_pem(app.state.signing_key)
    app.state.key_id = settings.key_id
    app.state.tenant_names = tenant_names
    logger.info("AegisTrace backend started (db=%s)", settings.database_url.split("@")[-1])
    try:
        yield
    finally:
        engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AegisTrace API",
        version="0.1.0",
        description="Continuous AI execution attestation and runtime causal trust.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(v1_router)

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/readyz", include_in_schema=False)
    async def readyz() -> JSONResponse:
        try:
            with app.state.session_factory() as db:
                db.execute(text("SELECT 1"))
            return JSONResponse({"status": "ready"})
        except Exception as e:  # pragma: no cover
            return JSONResponse({"status": "not-ready", "error": str(e)}, status_code=503)

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> PlainTextResponse:
        return PlainTextResponse(app.state.metrics.render())

    return app


app = create_app()
