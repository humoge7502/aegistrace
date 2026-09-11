"""SDK tests — embedded sink mode, @trace, steps, redaction, integrations."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import aegistrace
from aegistrace.integrations import mcp as at_mcp
from aegistrace.integrations import rag as at_rag
from aegistrace.integrations import tools as at_tools


class Sink:
    def __init__(self):
        self.batches: list[list[dict]] = []

    def __call__(self, batch: list[dict]) -> None:
        self.batches.append(batch)

    @property
    def events(self) -> list[dict]:
        return [e for b in self.batches for e in b]


def reset_sdk():
    aegistrace.context._client = None
    aegistrace.context._current.set(None)


def test_trace_decorator_records_full_execution():
    reset_sdk()
    sink = Sink()
    aegistrace.init(sink=sink, agent_ref="sdk-agent", agent_version="2.0")

    @aegistrace.trace
    def run_agent():
        with aegistrace.step("retrieval", "kb://docs") as s:
            s.record_documents([{"id": "d1", "text": "policy text"}])
        with aegistrace.step("mcp", "mcp://crm"):
            pass
        return "final answer"

    result = run_agent()
    assert result == "final answer"

    kinds = [e["kind"] for e in sink.events]
    assert kinds[0] == "execution.started"
    assert kinds.count("step.ended") == 2
    assert "output.produced" in kinds
    assert kinds[-1] == "execution.finished"

    output_evt = next(e for e in sink.events if e["kind"] == "output.produced")
    assert output_evt["payload"]["digest"].startswith("sha256:")
    # privacy: raw content must not appear anywhere
    assert all("final answer" not in str(e) for e in sink.events)


def test_exception_marks_failed():
    reset_sdk()
    sink = Sink()
    aegistrace.init(sink=sink)

    @aegistrace.trace
    def broken():
        raise RuntimeError("boom")

    try:
        broken()
    except RuntimeError:
        pass
    assert sink.events[-1]["kind"] == "execution.finished"
    assert sink.events[-1]["payload"]["status"] == "failed"


def test_pin_prompt_hashes():
    reset_sdk()
    sink = Sink()
    aegistrace.init(sink=sink)

    @aegistrace.trace
    def run():
        aegistrace.pin_prompt("system", "You are a helpful agent.")
        return "ok"

    run()
    pinned = next(e for e in sink.events if e["kind"] == "prompt.pinned")
    assert pinned["payload"]["hash"].startswith("sha256:")
    assert "helpful" not in str(sink.events)


class FakeCompletions:
    def create(self, **kwargs):
        class U:
            prompt_tokens = 10
            completion_tokens = 5
        class R:
            usage = U()
            id = "cmpl-123"
        return R()


class FakeOpenAIClient:
    def __init__(self):
        self.chat = type("Chat", (), {})()
        self.chat.completions = FakeCompletions()


def test_openai_integration_records_model_step():
    reset_sdk()
    from aegistrace.integrations import openai as at_openai
    sink = Sink()
    aegistrace.init(sink=sink)
    fake = FakeOpenAIClient()
    at_openai.instrument(fake)

    @aegistrace.trace
    def run():
        fake.chat.completions.create(model="gpt-4o-mini",
                                     messages=[{"role": "user", "content": "secret question"}])
        return "answer"

    run()
    model_step = next(e for e in sink.events if e["kind"] == "step.ended"
                      and e["payload"].get("kind") == "model")
    assert model_step["payload"]["target"] == "openai/gpt-4o-mini"
    assert model_step["payload"]["meta"]["prompt_hash"].startswith("sha256:")
    assert "secret question" not in str(sink.events)


class FakeMCPSession:
    def call_tool(self, name, arguments=None):
        return f"result-of-{name}"

    async def call_tool_async(self, name, arguments=None):  # pragma: no cover
        return "x"


def test_mcp_integration_records_steps():
    reset_sdk()
    sink = Sink()
    aegistrace.init(sink=sink)
    session = FakeMCPSession()
    at_mcp.instrument_session(session, "mcp://crm")

    @aegistrace.trace
    def run():
        session.call_tool("lookup_customer", {"id": 42})
        at_mcp.attest_server("mcp://crm", "1.0.0", "sha256:" + "2" * 64)
        return "done"

    run()
    mcp_steps = [e for e in sink.events if e["kind"] == "step.ended"
                 and e["payload"].get("kind") == "mcp"]
    assert len(mcp_steps) == 2
    assert mcp_steps[0]["payload"]["meta"]["tool"] == "lookup_customer"


def test_tools_decorator_and_rag():
    reset_sdk()
    sink = Sink()
    aegistrace.init(sink=sink)

    @at_tools.tool("send_email")
    def send_email(to: str, body: str) -> str:
        return "sent"

    @aegistrace.trace
    def run():
        at_rag.record_retrieval("kb://policies", [{"id": "d1", "text": "policy doc"}],
                                embedding_model="embed-v1")
        send_email(to="a@b.c", body="hello")
        return "ok"

    run()
    retrieval = next(e for e in sink.events if e["payload"].get("kind") == "retrieval")
    assert retrieval["payload"]["target"] == "kb://policies"
    assert retrieval["payload"]["meta"]["documents"][0]["hash"].startswith("sha256:")
    assert "policy doc" not in str(sink.events)
    tool_step = next(e for e in sink.events if e["payload"].get("kind") == "tool")
    assert tool_step["payload"]["target"] == "send_email"


def test_events_buffer_offline_and_flush():
    reset_sdk()
    # HTTP mode with unreachable endpoint: events stay buffered (fail-safe)
    aegistrace.init(endpoint="http://127.0.0.1:1", api_key="at_x")
    ctx = aegistrace.start_run(agent_ref="offline-agent")
    ctx.record_step("model", "m")
    client = aegistrace.get_client()
    pending = client.flush()  # failed post requeues
    assert client.pending() >= 1
    aegistrace.end_run()
