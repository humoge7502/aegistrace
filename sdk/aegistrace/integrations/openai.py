"""OpenAI integration — instrument a chat completions client.

Usage:
    from aegistrace.integrations import openai as at_openai
    at_openai.instrument(openai_client)

Every chat.completions.create call records a model step with the model identity
and hashed prompt. No raw content leaves the process (ADR-005).
"""

from __future__ import annotations

import functools
import threading

from aegistrace.context import current_run
from aegistrace.redaction import hash_content

_lock = threading.Lock()
_instrumented: set[int] = set()


def instrument(client) -> None:
    """Wrap client.chat.completions.create (idempotent per client instance)."""
    key = id(client)
    with _lock:
        if key in _instrumented:
            return
        _instrumented.add(key)
    original = client.chat.completions.create

    @functools.wraps(original)
    def wrapper(*args, **kwargs):
        run = current_run()
        if run is None:
            return original(*args, **kwargs)
        model = kwargs.get("model") or (args[0] if args else "unknown")
        messages = kwargs.get("messages")
        meta: dict = {"provider": "openai"}
        if messages:
            meta["prompt_hash"] = hash_content(messages)
            meta["message_count"] = len(messages)
        result = original(*args, **kwargs)
        if run is not None and not run.finished:
            usage = getattr(result, "usage", None)
            if usage is not None:
                meta["usage"] = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                }
            resp_id = getattr(result, "id", None)
            if resp_id:
                meta["completion_id"] = resp_id
            run.record_step("model", f"openai/{model}", meta=meta)
        return result

    client.chat.completions.create = wrapper


def uninstrument(client) -> None:
    """Test helper — restore the original method."""
    with _lock:
        _instrumented.discard(id(client))
