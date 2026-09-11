"""The @trace decorator — one-line agent instrumentation."""

from __future__ import annotations

import functools
from typing import Any, Callable

from aegistrace.context import current_run, end_run, start_run


def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap an agent entrypoint. Records execution.started / step events emitted
    inside / output.produced (hash of the return value) / execution.finished."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if current_run() is not None:
            # nested @trace: treat as a plain call to avoid double accounting
            return func(*args, **kwargs)
        start_run()
        try:
            result = func(*args, **kwargs)
            ctx = current_run()
            if ctx is not None:
                ctx.record_output(result)
            ctx = current_run()
            if ctx is not None:
                ctx.finish("completed")
            return result
        except BaseException:
            ctx = current_run()
            if ctx is not None:
                ctx.finish("failed")
            raise
        finally:
            end_run()

    return wrapper
