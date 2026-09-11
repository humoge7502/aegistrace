"""Anthropic integration — instrument a messages client."""

from __future__ import annotations

import functools
import threading

from aegistrace.context import current_run
from aegistrace.redaction import hash_content

_lock = threading.Lock()
_instrumented: set[int] = set()


def instrument(client) -> None:
    key = id(client)
    with _lock:
        if key in _instrumented:
            return
        _instrumented.add(key)
    original = client.messages.create

    @functools.wraps(original)
    def wrapper(*args, **kwargs):
        run = current_run()
        if run is None:
            return original(*args, **kwargs)
        model = kwargs.get("model") or (args[0] if args else "unknown")
        system = kwargs.get("system")
        messages = kwargs.get("messages")
        meta: dict = {"provider": "anthropic"}
        if system:
            meta["system_prompt_hash"] = hash_content(system)
        if messages:
            meta["prompt_hash"] = hash_content(messages)
        result = original(*args, **kwargs)
        usage = getattr(result, "usage", None)
        if usage is not None:
            meta["usage"] = {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
            }
        run.record_step("model", f"anthropic/{model}", meta=meta)
        return result

    client.messages.create = wrapper
