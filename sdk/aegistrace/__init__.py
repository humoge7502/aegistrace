"""AegisTrace Python SDK — minimal-change instrumentation for AI agents.

Usage:
    import aegistrace
    aegistrace.init(endpoint="http://127.0.0.1:8420", api_key="at_...")

    @aegistrace.trace
    def run_agent(question: str) -> str:
        with aegistrace.step("retrieval", "kb://policies") as s:
            docs = retrieve(question)
            s.record_documents(docs)
        with aegistrace.step("mcp", "mcp://crm"):
            ...
        return answer

Privacy: content is hashed (SHA-256) by default; nothing raw leaves the process
unless capture_content=True is passed explicitly (ADR-005).
"""

from aegistrace.client import CollectorClient
from aegistrace.context import RunContext, current_run, get_client, init, pin_prompt, start_run, step, end_run
from aegistrace.decorators import trace

__all__ = [
    "CollectorClient", "RunContext", "current_run", "get_client", "init", "pin_prompt",
    "start_run", "step", "end_run", "trace",
]
__version__ = "0.1.0"
