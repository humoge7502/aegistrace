"""MCP (Model Context Protocol) integration.

Two supported patterns:
1. Wrap a client session:  instrument_session(session, server="mcp://crm")
   records every session.call_tool(...) as an mcp step (tool name + hashed args).
2. Server-side fixture attestation:  attest_server(server_name, version, digest)
   records the server component identity for expected-vs-observed digest checks.
"""

from __future__ import annotations

import functools

from aegistrace.context import current_run
from aegistrace.redaction import hash_content


def instrument_session(session, server: str) -> None:
    """Wrap session.call_tool to record MCP tool invocations."""
    if getattr(session, "_aegistrace_instrumented", False):
        return
    original = session.call_tool

    @functools.wraps(original)
    async def async_wrapper(name, arguments=None, **kwargs):
        run = current_run()
        result = await original(name, arguments, **kwargs)
        if run is not None and not run.finished:
            run.record_step("mcp", server, meta={
                "tool": name,
                "args_hash": hash_content(arguments or {}),
            })
        return result

    @functools.wraps(original)
    def sync_wrapper(name, arguments=None, **kwargs):
        run = current_run()
        result = original(name, arguments, **kwargs)
        if run is not None and not run.finished:
            run.record_step("mcp", server, meta={
                "tool": name,
                "args_hash": hash_content(arguments or {}),
            })
        return result

    import inspect
    session.call_tool = async_wrapper if inspect.iscoroutinefunction(original) else sync_wrapper
    session._aegistrace_instrumented = True


def attest_server(server_name: str, version: str, digest: str) -> None:
    """Attest the MCP server component identity (digest of its code/config)."""
    run = current_run()
    if run is not None and not run.finished:
        run.record_step("mcp", server_name, digest=digest, version=version)


def attest_tool(tool_name: str, digest: str | None = None, version: str | None = None) -> None:
    """Record a tool invocation with its identity digest."""
    run = current_run()
    if run is not None and not run.finished:
        run.record_step("tool", tool_name, digest=digest, version=version)
