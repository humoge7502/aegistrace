"""Application configuration.

All settings are environment-driven (12-factor). Secrets are never hard-coded;
the bootstrap dev key is generated and printed once unless explicitly provided.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGISTRACE_", env_file=None)

    # --- storage ---
    database_url: str = f"sqlite:///{(REPO_ROOT / 'backend' / 'data' / 'aegistrace.db').as_posix()}"

    # --- signing ---
    signing_key_path: Path = REPO_ROOT / "backend" / "keys" / "at_ed25519.pem"
    key_id: str = "aegistrace-dev-1"

    # --- bootstrap ---
    bootstrap_key: str | None = None  # if unset, a random dev key is generated and printed

    # --- privacy ---
    allow_content: bool = False  # when False, backend rejects events carrying raw content

    # --- rate limiting (simple in-process token bucket; single-instance only) ---
    rate_limit_per_minute: int = 600

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # --- misc ---
    log_level: str = "INFO"
    retention_days: int = 365


@lru_cache
def get_settings() -> Settings:
    return Settings()
