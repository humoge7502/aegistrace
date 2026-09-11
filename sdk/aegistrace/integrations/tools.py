"""Tool decorator — record local tool/function invocations as steps."""

from __future__ import annotations

import functools
from typing import Any, Callable

from aegistrace.context import current_run
from aegistrace.redaction import hash_content


def tool(name: str | None = None, digest: str | None = None) -> Callable:
    """Decorator: @aegistrace.tool("send_email") — records a tool step with
    hashed arguments on every call while a run is active."""
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            run = current_run()
            result = func(*args, **kwargs)
            if run is not None and not run.finished:
                run.record_step("tool", tool_name, digest=digest, meta={
                    "args_hash": hash_content({"args": args, "kwargs": kwargs}),
                })
            return result

        return wrapper
    return decorator
