# AegisTrace

**Continuous AI Execution Attestation & Runtime Causal Trust**

AegisTrace continuously constructs a machine-readable provenance graph of every component
that influences an AI/agent execution — model, prompt, retrieval, tools, MCP servers,
dependencies, runtime — compares the **observed** execution against the **expected**
execution contract, propagates trust and compromise through causal dependencies, and
issues verifiable per-execution **AI Trust Certificates**.

It answers, for any AI output:

> Which trusted components caused this output, what was their state at execution time,
> did the execution path deviate from its expected state, and can we cryptographically
> and causally prove whether the output should be trusted?

---

## Repository layout

| Path | Contents |
|---|---|
| `backend/` | FastAPI service: provenance ingestion, causal graph, expected-vs-observed deviation detection, trust propagation, policy engine, certificates, incidents, audit |
| `sdk/` | `aegistrace` Python SDK (`@aegistrace.trace`, integrations for OpenAI / Anthropic / MCP / RAG / tools) |
| `frontend/` | Next.js console (overview, executions, trust graph, incidents, certificates, AttackBench) |
| `benchmarks/` | AegisBench performance harness + AttackBench detection suite + baseline comparison |
| `demo/` | Reproducible end-to-end killer demo |
| `docs/` | Architecture, research, threat model, design system, task board, ADRs, final report |

## Quickstart (local, no external services)

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash (Linux/macOS: source .venv/bin/activate)
pip install -e ./backend -e ./sdk

# start the API (SQLite by default; set DATABASE_URL for PostgreSQL)
uvicorn backend.app.main:app --port 8420

# run the killer demo (normal → compromise → detection → quarantine → recovery → re-certify)
python demo/killer_demo.py
```

Default dev bootstrap creates tenant `local` with admin API key printed at startup
(override with `AEGISTRACE_BOOTSTRAP_KEY`). **Unknown ≠ trusted**: executions without
sufficient evidence are marked `UNKNOWN`, never silently trusted.

## Tests

```bash
pytest backend/tests -q
```

## Status

See `docs/FINAL-REPORT.md` (VERIFIED / PROPOSED / UNVERIFIED classification of all
claims), `docs/agent-state/PROJECT-STATE.md`, and `docs/tasks/TASK-BOARD.md`.
