# AegisTrace Python SDK

Package: `sdk/` (install with `pip install -e ./sdk`).

## Quickstart

```python
import aegistrace

aegistrace.init(
    endpoint="http://127.0.0.1:8420",
    api_key="at_...",                 # role=agent key (ingest-only)
    agent_ref="support-agent",
    agent_version="1.0.0",
)

@aegistrace.trace
def run_agent(question: str) -> str:
    with aegistrace.step("retrieval", "kb://policies") as s:
        docs = retrieve(question)
        s.record_documents(docs)              # reduced to (id, sha256) refs

    with aegistrace.step("mcp", "mcp://crm", digest=mcp_digest):   # digest = component identity
        result = mcp_client.call_tool("lookup_customer", {"id": 42})

    with aegistrace.step("tool", "tool:send_email"):
        send_email(...)
    return draft_reply                         # output hashed automatically
```

The decorator emits: `execution.started` → your steps → `output.produced`
(sha256 of the return value) → `execution.finished`. The backend compares the
observed graph against the agent's registered **baseline** and decides trust.

## Privacy (ADR-005)

- All content is SHA-256 hashed by default; raw text never leaves the process.
- `pin_prompt(role, text)` records only the hash.
- Explicit content capture requires `capture_content=True` per call *and*
  `AEGISTRACE_ALLOW_CONTENT=true` server-side.

## API surface

| Symbol | Purpose |
|---|---|
| `init(endpoint, api_key, agent_ref, agent_version, sink=None, capture_content=False)` | configure the collector; pass `sink=` (callable) for embedded/offline mode |
| `trace` | decorator for agent entrypoints |
| `start_run()/end_run()` | manual run lifecycle (non-decorator usage) |
| `step(kind, target, digest=None, meta=None, version=None)` | context manager recording a step (`kind ∈ model, retrieval, tool, mcp, api, embedding, runtime, package, custom`) |
| `StepSpan.record_documents(docs)` | attach (id, sha256) document refs to a retrieval step |
| `pin_prompt(role, text)` | pin a prompt hash for the current run |
| `current_run()` | active `RunContext` (advanced use) |

### Integrations (`aegistrace.integrations`)

| Module | Call | Effect |
|---|---|---|
| `openai` | `instrument(client)` | every `chat.completions.create` → `model` step with model id + hashed messages + usage |
| `anthropic` | `instrument(client)` | every `messages.create` → `model` step (hashed system + messages) |
| `mcp` | `instrument_session(session, server)` | every `call_tool` → `mcp` step (tool + hashed args); `attest_server(name, version, digest)` for component identity |
| `rag` | `record_retrieval(index_id, docs, embedding_model)` | retrieval step with document refs |
| `tools` | `@tool(name)` | tool invocation step with hashed arguments |

## Fail-safe behavior

Transport failures requeue events client-side (bounded buffer). Executions the
backend never hears about are simply unattested — the server defaults unknown
agents to `UNKNOWN`, never `TRUSTED`.
