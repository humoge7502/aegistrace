# AegisTrace — Project State

_Updated: 2026-09-12. Every agent must read this file before modifying code, and update
it after completing a meaningful task._

## Current phase

P0 core implementation (provenance → expected/observed → deviation → trust propagation →
output trust determination → certificates → killer demo), then P1, then frontend polish,
benchmarks, and final audit.

## Architecture snapshot

- Modular monolith: FastAPI backend (`backend/app`), SQLAlchemy 2.0 ORM.
  - Dev/test: SQLite (`backend/data/aegistrace.db`). Prod: PostgreSQL via `DATABASE_URL`.
  - Alembic migrations in `backend/alembic/`; tests use `create_all` for speed.
- Causal graph stored relationally (`edges` table: src/dst typed references + kind +
  observed-in-execution + timestamp). Recursive CTEs for impact analysis (works on
  SQLite and PostgreSQL).
- Trust engine: component trust states + propagation over causal edges; every decision
  stored with a full evidence chain (no opaque scores).
- Certificates: Ed25519-signed, in-toto Statement v1 layout with custom predicate type
  `https://aegistrace.dev/attestations/execution-trust/v1`; revocation list on compromise.
- SDK: `aegistrace` Python package, `@trace` decorator + step context managers +
  integrations (OpenAI, Anthropic, MCP, RAG, tools). Hash-by-default redaction.
- Frontend: Next.js (App Router) + Tailwind v4, design system in
  `docs/design/aegistrace-design-system.md` (original "Ledger" identity).

## Decisions log

See `docs/decisions/ADR-index.md` (ADRs 001–006).

## Known bugs / open questions

- OPEN Q-1: Docker daemon unavailable on the dev machine — compose stack documented but
  not yet run end-to-end (marked UNVERIFIED until run).
- OPEN Q-2: Real LLM calls are not exercised in demo (simulated model fixture); provider
  integrations are tested against stubs. Real-provider smoke tests are deferred P2.
- OPEN Q-3: Patent counsel review required before any IP filing (see
  `docs/research/prior-art.md` — technical hypotheses only).

## Deferred work

- Multi-language SDKs (TypeScript next).
- Neo4j/graph-DB backend (only if relational proven insufficient — ADR-002).
- Kafka/Redpanda event bus (only at high ingest volume — ADR-001).
- Sigstore keyless signing for certificates (currently Ed25519 local keys; Sigstore
  integration designed, not implemented).
