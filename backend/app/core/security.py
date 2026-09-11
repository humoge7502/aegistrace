"""API-key authentication, rate limiting, and redaction helpers."""

from __future__ import annotations

import hashlib
import re
import secrets
import threading
import time

# --- API keys ---------------------------------------------------------------

KEY_PREFIX = "at"


def generate_api_key() -> str:
    return f"{KEY_PREFIX}_{secrets.token_urlsafe(32)}"


def key_prefix(key: str) -> str:
    return key[:10]


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


# --- redaction (defense in depth; the SDK already hashes by default) --------

CONTENT_KEYS = {"content", "text", "body", "message", "messages", "prompt", "documents",
                "document", "args", "arguments", "input", "output_text", "value"}

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|authorization)\s*[:=]\s*\S+"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),  # OpenAI-style keys
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def looks_like_secret(value: str) -> bool:
    return any(p.search(value) for p in _SECRET_PATTERNS)


def redact_strings(obj: object) -> object:
    """Replace secret-looking strings with a marker (used on metadata, not content)."""
    if isinstance(obj, str):
        if looks_like_secret(obj):
            return "[REDACTED]"
        return obj
    if isinstance(obj, dict):
        return {k: redact_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_strings(v) for v in obj]
    return obj


# --- rate limiting (single-instance token bucket per API key) ----------------

class TokenBucket:
    def __init__(self, per_minute: int) -> None:
        self.capacity = max(1, per_minute)
        self.tokens = float(self.capacity)
        self.refill_rate = self.capacity / 60.0
        self.updated = time.monotonic()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.refill_rate)
            self.updated = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False


class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def allow(self, subject: str) -> bool:
        with self._lock:
            bucket = self._buckets.get(subject)
            if bucket is None:
                bucket = TokenBucket(self.per_minute)
                self._buckets[subject] = bucket
        return bucket.allow()
