"""Run context — per-execution collection state (ContextVar-based)."""

from __future__ import annotations

import itertools
import uuid
from contextvars import ContextVar
from types import TracebackType

from aegistrace.client import CollectorClient
from aegistrace.redaction import document_refs, hash_content

_current: ContextVar["RunContext | None"] = ContextVar("aegistrace_run", default=None)

_client: CollectorClient | None = None
_agent_ref: str = "unknown-agent"
_agent_version: str | None = None
_capture_content: bool = False


def init(
    endpoint: str | None = None,
    api_key: str | None = None,
    sink=None,
    agent_ref: str = "unknown-agent",
    agent_version: str | None = None,
    capture_content: bool = False,
) -> CollectorClient:
    """Configure the global collector. HTTP mode (endpoint+api_key) or embedded
    sink (callable receiving event batches — used by tests and offline tools)."""
    global _client, _agent_ref, _agent_version, _capture_content
    _client = CollectorClient(endpoint=endpoint, api_key=api_key, sink=sink)
    _agent_ref = agent_ref
    _agent_version = agent_version
    _capture_content = capture_content
    return _client


def get_client() -> CollectorClient:
    if _client is None:
        raise RuntimeError("aegistrace.init() was not called")
    return _client


class RunContext:
    def __init__(self, agent_ref: str | None = None, agent_version: str | None = None,
                 run_id: str | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:16]
        self.agent_ref = agent_ref or _agent_ref
        self.agent_version = agent_version or _agent_version
        self._seq = itertools.count(1)
        self.finished = False
        self._client = get_client()
        self.emit("execution.started", {"agent_ref": self.agent_ref,
                                        "agent_version": self.agent_version})

    @property
    def client(self) -> CollectorClient:
        return self._client

    def next_seq(self) -> int:
        return next(self._seq)

    def emit(self, kind: str, payload: dict, external_id: str | None = None) -> None:
        self._client.emit({
            "kind": kind,
            "execution_external_id": external_id or self.run_id,
            "payload": payload,
        })

    def record_step(self, kind: str, target: str, digest: str | None = None,
                    meta: dict | None = None, version: str | None = None) -> dict:
        payload: dict = {"seq": self.next_seq(), "kind": kind, "target": target}
        if digest:
            payload["digest"] = digest
        if version:
            payload["version"] = version
        if meta:
            payload["meta"] = meta
        self.emit("step.ended", payload)
        return payload

    def record_documents(self, refs: list[dict]) -> None:
        """Attach retrieved-document references to the most recent retrieval step
        (emitted as part of the step's meta on the next step event is complex;
        instead we attest the corpus component with doc hashes)."""
        self.emit("component.observed", {
            "kind": "document",
            "name": "retrieved-documents",
            "meta": {"documents": refs},
        })

    def record_output(self, output: object, output_kind: str = "text",
                      output_id: str | None = None) -> str:
        digest = hash_content(output)
        payload: dict = {"digest": digest, "output_kind": output_kind}
        if output_id:
            payload["output_id"] = output_id
        if _capture_content and isinstance(output, str):
            payload["content"] = output
        self.emit("output.produced", payload)
        return digest

    def pin_prompt(self, role: str, content: object) -> str:
        digest = hash_content(content)
        self.emit("prompt.pinned", {"role": role, "hash": digest})
        return digest

    def finish(self, status: str = "completed") -> None:
        if self.finished:
            return
        self.finished = True
        self.emit("execution.finished", {"status": status}, external_id=self.run_id)
        self._client.flush()


def start_run(agent_ref: str | None = None, agent_version: str | None = None,
              run_id: str | None = None) -> RunContext:
    ctx = RunContext(agent_ref=agent_ref, agent_version=agent_version, run_id=run_id)
    _current.set(ctx)
    return ctx


def end_run() -> None:
    _current.set(None)


def current_run() -> RunContext | None:
    return _current.get()


def step(kind: str, target: str, digest: str | None = None, meta: dict | None = None,
         version: str | None = None) -> "StepSpan":
    """Record a step (context manager). Usage:
        with aegistrace.step("mcp", "mcp://crm", digest="sha256:..."):
            ...
    """
    return StepSpan(kind, target, digest=digest, meta=meta, version=version)


def pin_prompt(role: str, content: object) -> str | None:
    ctx = _current.get()
    if ctx is None:
        return None
    return ctx.pin_prompt(role, content)


class StepSpan:
    def __init__(self, kind: str, target: str, digest: str | None = None,
                 meta: dict | None = None, version: str | None = None) -> None:
        self.kind = kind
        self.target = target
        self.digest = digest
        self.meta = meta or {}
        self.version = version
        self._ctx: RunContext | None = None
        self.documents: list[dict] = []

    def record_documents(self, documents: list) -> "StepSpan":
        self.documents = document_refs(documents)
        return self

    def __enter__(self) -> "StepSpan":
        self._ctx = _current.get()
        return self

    def __exit__(self, exc_type, exc, tb: TracebackType | None) -> bool:
        if self._ctx is None:
            return False
        meta = dict(self.meta)
        if self.documents:
            meta["documents"] = self.documents
        self._ctx.record_step(self.kind, self.target, digest=self.digest,
                              meta=meta or None, version=self.version)
        return False
