# ADR Index — AegisTrace

Status legend: accepted | proposed | superseded

## ADR-001: Modular monolith first; SQLite for dev/test, PostgreSQL for prod; no event bus yet — ACCEPTED

Context: we need causal graph ingestion, deviation detection, and trust propagation with
strong consistency for the core thesis; operational sprawl (Kafka, many services) would
delay validation of the thesis itself.

Decision: single FastAPI service; SQLAlchemy 2.0; SQLite for local dev/tests,
PostgreSQL in deployment via `DATABASE_URL`; synchronous ingestion path with in-process
batching. Kafka/Redpanda deferred until measured ingest volume justifies it.

Consequences: simplest reproducible path; vertical-scale ceiling documented; interfaces
(`collect.ingest`, `graph.service`) keep ingestion side-effect-free from storage details
so an async worker can be extracted later.

## ADR-002: Relational causal graph (edges table + recursive CTEs), not a graph database — ACCEPTED

Context: the graph is dominated by per-execution linear step chains plus component usage
edges; queries needed are ancestry (what influenced this output), descendants (what
depends on this component), and time-windowed traversal.

Decision: store nodes as typed references to existing entities (components, executions,
outputs) and edges in a single `edges` table; impact queries via recursive CTEs (supported
by SQLite ≥3.8.3 and PostgreSQL). Revisit Neo4j only if measured query latency at realistic
volume (>10M edges) fails targets.

## ADR-003: Expected-state contract = "Execution Baseline" with sequence + allowed-set modes — ACCEPTED

Context: AI executions are probabilistic; an exact single-path expectation produces false
positives.

Decision: a Baseline declares (a) an expected ordered `steps` list used in `sequence`
mode, (b) `allowed` component sets (tools, MCP, retrieval, model) used in `allowed_set`
mode, (c) `component_digests` verified for every attested component, (d) optional
`prompt_hashes` for prompt pinning. Deviations classify as: digest_mismatch (critical),
unexpected_component (critical), path_deviation (high), missing_step (medium),
stale_evidence (medium). Trust defaults: any critical → UNTRUSTED; high → DEGRADED;
no baseline under strict policy → UNKNOWN (never silently trusted).

## ADR-004: AI Trust Certificates are Ed25519-signed in-toto Statement v1 documents with a custom predicate — ACCEPTED

Context: verifiability and standards interoperability are requirements; do not invent a
crypto envelope.

Decision: certificate payload is an in-toto Statement v1 JSON:
`_type = "https://in-toto.io/Statement/v1"`, `subject = [{name: execution:<id>, digest:
{sha256: <fingerprint>}}]`, `predicateType =
"https://aegistrace.dev/attestations/execution-trust/v1"`, `predicate = {trust_state,
checks, evidence, baseline_ref, issued_at, issuer}`. Signing: Ed25519 over canonical
(UTF-8, sort_keys) JSON. Revocation: certificate row → REVOKED with reason; verification
endpoint checks signature + revocation + subject digest match. Sigstore/keyless signing
is designed (OID-token backed) but not implemented — tracked as future work.

## ADR-005: Privacy — hash-by-default collection with explicit content opt-in — ACCEPTED

Context: collectors see prompts, retrieved documents, tool arguments.

Decision: SDK hashes all content (SHA-256) by default; raw content leaves the process
only when a step explicitly opts in (`capture_content=True`) or the operator enables
`AEGISTRACE_ALLOW_CONTENT=true` on the backend; per-tenant retention policy stored;
secrets patterns (env-var values, anything matching common key formats) are redacted
before serialization.

## ADR-006: AuthN = per-tenant API keys (roles admin/operator/agent/viewer), AuthZ enforced server-side — ACCEPTED

Context: enterprise SSO/OIDC is required eventually but not to validate the thesis.

Decision: API keys (hashed with SHA-256, prefix shown for identification) with roles;
tenant scoping enforced in every query; agent-role keys can only ingest events and read
their own execution status; all mutating calls audit-logged. OAuth/OIDC designed for P2.
Bootstrap dev key is printed once at first startup and must be rotated (`AEGISTRACE_BOOTSTRAP_KEY`).
