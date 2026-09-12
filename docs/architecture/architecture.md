# AegisTrace — Architecture

_Status: v1.0 (2026-09-12). ADRs: `docs/decisions/ADR-index.md`._

## 1. System overview

AegisTrace is a modular monolith with four logical planes:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  AGENT PLANE (customer side)                                             │
│  Python SDK  ── @trace, step spans, prompt pinning, output hashing       │
│  integrations ─ OpenAI / Anthropic / MCP / RAG / tools                   │
│  privacy      ─ hash-by-default redaction (ADR-005)                      │
└───────────────┬──────────────────────────────────────────────────────────┘
                │ HTTPS  POST /api/v1/events/batch  (X-API-Key, role=agent)
┌───────────────▼──────────────────────────────────────────────────────────┐
│  INGESTION PLANE (backend/app/collect)                                   │
│  event validation → raw append-only log → redaction (defense in depth)   │
│  → per-event flush (transactional batch)                                 │
└───────────────┬──────────────────────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────────────────────┐
│  CAUSAL GRAPH PLANE (backend/app/graph)                                  │
│  components (identity + expected/observed digests + trust state)         │
│  executions (ordered steps, canonical fingerprint)                       │
│  edges (execution -step→ component, execution -produced→ output)         │
│  baselines (expected contract: sequence / allowed_set / policy_only)     │
│  deviation detection: digest_mismatch | unexpected_component |           │
│    path_deviation | missing_step | prompt_mismatch | missing_provenance  │
└───────────────┬──────────────────────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────────────────────┐
│  TRUST PLANE (backend/app/trust, policy, certs)                          │
│  trust engine: explainable decisions + causal propagation                │
│    component COMPROMISED → executions → outputs → certificates revoked   │
│  policy engine: severity→state mapping, quarantine, certification rules  │
│  certificates: Ed25519-signed in-toto Statement v1 (ADR-004)             │
│  incidents + quarantine actions + audit log                              │
└───────────────┬──────────────────────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────────────────────┐
│  INTERFACE PLANE                                                         │
│  REST API v1 (typed, versioned)      Next.js console (trust graph UI)    │
└──────────────────────────────────────────────────────────────────────────┘
```

## 2. Core domain model

Entities (SQLAlchemy, `backend/app/domain/models.py`): `Tenant`, `ApiKey`, `Policy`,
`Component`, `Baseline`, `Execution`, `Output`, `Edge`, `RawEvent`, `IntegrityEvent`,
`TrustDecision`, `Certificate`, `Incident`, `QuarantineAction`, `AuditLog`,
`MetricSample`.

Trust states (`TRUSTED`, `UNTRUSTED`, `UNKNOWN`, `DEGRADED`, `COMPROMISED`,
`QUARANTINED`, `RECOVERING`, `RE-CERTIFIED`) — full state semantics in
`docs/architecture/trust-model.md`.

## 3. The causal graph

- Nodes are typed references: `(component|execution|output, uuid)`.
- Edges: `execution -step(seq)→ component`, `execution -produced→ output`,
  `component -depends_on→ component` (reserved).
- Impact queries traverse `edges` with recursive CTEs (ADR-002):
  - "What influenced this output?" — reverse walk from output → execution → components.
  - "What depends on this component?" — forward walk component → executions → outputs.
- Every edge records `execution_id`, `seq`, `expected`, `ts` — the evidence that
  makes trust decisions explainable.

## 4. Expected vs observed

A **Baseline** is the expected execution contract (ADR-003): ordered steps,
allowed component sets, pinned component digests, pinned prompt hashes.
Comparison at `execution.finished` produces **IntegrityEvents** classified:

| Kind | Default severity | Trigger |
|---|---|---|
| `digest_mismatch` | critical | observed component digest ≠ pinned digest |
| `unexpected_component` | critical | component outside allow-list / expected path |
| `path_deviation` | high | observed sequence ≠ expected sequence |
| `missing_step` | medium | expected step never observed |
| `prompt_mismatch` | critical | prompt hash ≠ pinned hash |
| `missing_provenance` | medium | execution finished with zero steps |

## 5. Trust decisions and propagation

`decide_execution` maps worst-severity → state per tenant policy
(critical/high → UNTRUSTED, medium/low → DEGRADED, no baseline → UNKNOWN,
zero evidence → UNKNOWN — **UNKNOWN ≠ TRUSTED**). Runs marked `rerun_of` that
pass all checks become `RE-CERTIFIED`.

`compromise_component` walks the causal graph and, for every affected execution:
writes a TrustDecision with the full hop chain, invalidates the execution,
quarantines dependent outputs, revokes ACTIVE certificates, creates/updates an
Incident with evidence, and records QuarantineActions. Scope is all-history by
default (`compromised_propagation: from_compromise_time` available).

## 6. Certificates

in-toto Statement v1 with predicate type
`https://aegistrace.dev/attestations/execution-trust/v1`; subject = execution
fingerprint; signed with Ed25519 over canonical JSON. Verification = signature +
revocation status + subject-vs-current-fingerprint match. Sigstore keyless
signing is designed (ADR-004) but not implemented.

## 7. Security architecture

- AuthN: per-tenant API keys (SHA-256 hashed), roles admin/operator/agent/viewer;
  agent keys are ingest-only.
- AuthZ: enforced server-side per endpoint; tenant scoping on every query.
- Audit: all mutations logged (actor, action, object, detail).
- Rate limiting: per-key token bucket (single-instance).
- Headers: nosniff, DENY framing, no-referrer, no-store. CORS restricted.
- Privacy: hash-by-default (SDK), backend re-sanitization, opt-in content only.
- Threat model: `docs/security/threat-model.md`.

## 8. Scaling path (deliberate, measured)

Current numbers: see `docs/benchmarks/perf-results.json`. Identified extraction
points when needed: (1) ingestion → async workers + Kafka/Redpanda; (2) impact
queries → materialized closure table or graph DB (only if measured need);
(3) metrics → OpenTelemetry collector. No premature microservices (ADR-001).
