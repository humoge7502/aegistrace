# AegisTrace — Final Report

_Date: 2026-09-12 · Version 0.1.0 (first major milestone)_
_Every claim below is tagged: **[VERIFIED]** (demonstrated in this repo, reproducible),
**[PROPOSED]** (designed, not yet implemented), **[UNVERIFIED]** (not run / needs external validation)._

---

## 1. Executive summary

AegisTrace is a working platform for **continuous AI execution attestation and
runtime causal trust**. It ingests provenance events from a Python SDK, builds a
relational causal graph of every component influencing an AI execution, verifies
the observed execution against a registered expected contract, classifies
deviations, propagates compromise through causal dependencies to outputs and
certificates, and issues verifiable per-execution **AI Trust Certificates**
(Ed25519-signed in-toto statements).

The definitive experiment — *can AegisTrace detect a compromised AI execution
whose output looks normal?* — **[VERIFIED]**: the killer demo and the test suite
both demonstrate an execution with an inserted attacker-controlled MCP call
producing an indistinguishable output, flagged `UNTRUSTED` by execution-path
deviation with full evidence of what changed, where, and what was affected.

Empirical differentiation vs simpler approaches **[VERIFIED on the AttackBench
fixture set]**: on identical fixtures, an SBOM-only strategy detects 36% of the
14 attack scenarios, digest-attestation-only 64%, provenance-without-expectations
0% (it records but cannot flag), while the full pipeline detects 100% with zero
false positives on benign controls.

## 2. Architecture

Modular monolith (ADR-001): FastAPI + SQLAlchemy 2.0; SQLite for dev/test,
PostgreSQL-ready. Planes: SDK/agent → ingestion → causal graph (expected vs
observed) → trust engine (decisions + propagation) → certificates/policy →
REST v1 + Next.js console. Details: `docs/architecture/architecture.md`.
**[VERIFIED]** as implemented and exercised end-to-end over HTTP.

## 3. Technology decisions

Python 3.13, FastAPI, SQLAlchemy 2.0 (recursive-CTE graph on SQLite/Postgres —
ADR-002), Ed25519 via `cryptography`, Pydantic v2 event contracts, Next.js 16 +
Tailwind v4 + custom SVG graph (no heavy graph deps), Playwright for UI
verification. Rationale in ADR-001..006. **[VERIFIED: all in use]**

## 4. Implemented capabilities (all VERIFIED unless noted)

1. **Machine-readable provenance** — event vocabulary v1
   (`docs/architecture/provenance-spec.md`), append-only raw log, replayable.
2. **Expected-state baselines** — sequence / allowed_set / policy_only modes;
   pinned component digests and prompt hashes.
3. **Runtime integrity verification** — digest mismatch, unexpected component,
   path deviation, missing step, prompt mismatch, missing provenance.
4. **Causal execution graph** — ordered step edges, produced edges, deviation
   flags, fingerprint = certificate subject.
5. **Execution fingerprints** — canonical sha256 over ordered step signatures.
6. **Explainable trust propagation** — component compromise → affected
   executions → outputs → certificate revocation, each hop evidenced; incident
   with full affected lists.
7. **Output dependency tracing & invalidation** — "what depends on this
   component?" live view + historical invalidation with quarantine.
8. **Quarantine & recovery** — quarantine actions recorded; recovery restores
   component trust with digest verification; historical outputs are never
   silently re-trusted (re-execution only).
9. **Re-certification** — `rerun_of` runs passing all checks become
   `RE-CERTIFIED` with a fresh certificate.
10. **Verifiable certificates** — Ed25519 over canonical JSON, in-toto Statement
    v1 predicate `https://aegistrace.dev/attestations/execution-trust/v1`,
    verify = signature + revocation + subject match; forgery rejected
    (AttackBench forged-attestation).
11. **Policy engine** — severity→state mapping, quarantine/certification
    switches, per-tenant rows, admin-audited updates.
12. **Security** — API keys (hashed) with ingest-only agent role, tenant
    isolation (tested), rate limiting, audit log, security headers, hash-by-
    default redaction with backend re-sanitization.
13. **SDK** — `@trace`, step spans, prompt pinning, OpenAI/Anthropic/MCP/RAG/tool
    integrations, HTTP + embedded transports, offline buffering.
14. **Console** — landing, API-key login, overview, executions, execution detail
    with interactive SVG trust graph (pan/zoom/keyboard/ARIA + text
    alternative), components with compromise/recover/impact, incidents,
    certificates with verify, AttackBench viewer, settings/policy/keys/audit.
    Visual acceptance: judge-reviewed, 9/9 pages pass after 3 fix rounds
    (`docs/ui-screens/`).
15. **Benchmarks** — AttackBench (17 fixtures, precision/recall 1.0), baseline
    comparison, perf harness; all reproducible single-command.
16. **Migrations & CI** — Alembic initial migration (drift-checked), GitHub
    Actions running tests + AttackBench regression gate + builds.

## 5. Provenance / causal graph / trust models

Summarized in `docs/architecture/provenance-spec.md`, `trust-model.md`;
state machine, decision inputs, propagation semantics, failure posture.

## 6. Runtime monitoring

SDK-collected (component digests at execution time, ordered steps, document
hashes, prompt hashes, outputs). Host-level collection (eBPF/syscall, process
integrity) is **[PROPOSED]** — designed as the P2 runtime agent, not implemented.

## 7. Security architecture

Threat model: `docs/security/threat-model.md` (STRIDE per plane + AI abuse-case
matrix mapped to AttackBench). Honest limitations documented (fully compromised
client host can lie about local execution; digest pinning is tofu-style at
registration; single-instance limiter/metrics; no DB hash-chaining yet).

## 8. AttackBench

14 attack scenarios (model/prompt/dataset/dependency/container/RAG/tool/MCP/
runtime tampering, path deviation, multi-component, forged attestation, stale
trust, historical compromise) + 3 benign controls. Precision 1.0, recall 1.0.
All fixtures harmless local simulations. **[VERIFIED]**, with the
methodology caveat in `docs/benchmarks/methodology.md`: fixtures and detectors
share authors — external adversarial review is required before any external
performance claim.

## 9. Experimental results

| Result | Value | Source |
|---|---|---|
| Test suite | 48 passed (unit/integration/security/SDK/E2E + audit regressions) | `pytest backend/tests` |
| AttackBench | P=1.0 R=1.0 Acc=1.0 | `docs/benchmarks/attackbench-results.json` |
| Baseline comparison | sbom 0.36 / attestation 0.64 / provenance 0.0 / full 1.0 recall | `docs/benchmarks/comparison.md` |
| Ingest throughput | ~88–130 events/s (varies by run) | `docs/benchmarks/perf-results.json` |
| Propagation (200 exec) | ~0.9–1.1 s, 200 outputs, 200 certs | same |
| Impact query | ~460–470 ms | same |
| Schema drift | 0 (alembic autogenerate empty) | this audit |

All numbers from this machine (Windows, SQLite, in-process engine) — regenerate
on target hardware. **[VERIFIED as reproducible scripts]**

## 10. Comparison with existing approaches

`docs/benchmarks/comparison.md` (empirical, capability-level) +
`docs/research/competitive-analysis.md` (qualitative, sourced). The measured
white space: expected-vs-observed execution-graph verification, causal trust
propagation to outputs, and signed per-execution certificates.

## 11. Known limitations

1. Client-host compromise can fabricate plausible events (mitigated by
   server-side expected-state checks, not eliminated) — see threat model §5.
2. TEE/measured-boot runtime attestation **[PROPOSED]**, not implemented.
3. Replay hardening (per-event nonces) **[PROPOSED]**.
4. Single-instance rate limiting/metrics; OTel export optional **[PROPOSED]**.
5. Real-provider smoke tests (OpenAI/Anthropic live) **[UNVERIFIED]** —
   integrations are tested against stubs; no API keys in this environment.
6. Docker compose stack **[UNVERIFIED]** — daemon unavailable during the build
   session; Dockerfiles + compose provided, CI covers Linux test paths.
7. Baseline registration governance (who pins digests) is process, not product.

## 12. Research hypotheses (technical, NOT legal conclusions)

From `docs/research/white-space.md` — ranked white-space hypotheses with
falsifiers: (1) expected-vs-observed execution-graph verification; (2) trust
propagation → output quarantine/invalidation/re-certification; (3) signed
per-execution trust certificates; (4) AI-native provenance benchmark
(AttackBench). Closest prior art identified: HOLMES/NoDoze/RapSheet (host-level
provenance-graph detection), PROV-AGENT (capture/query only, explicitly names
invalidation/quarantine as open gaps), AgentSign (signed chains; HN critique —
signatures prove what was sent, not that the signer was uncompromised — is
exactly the gap AegisTrace targets). Patent landscape mapped (12 items) —
**professional patent counsel required before any filing; nothing here asserts
patentability.**

## 13. Prior-art findings

`docs/research/prior-art.md` — academic (provenance-graph IDS lineage), standards
(SLSA v1.2, in-toto ITE-6, Sigstore, CycloneDX 1.6 AI/ML BOM, OTel GenAI semconv,
EU AI Act Art. 12/19 logging hooks), commercial landscape incl. the 2024–2025
consolidation wave (Robust Intelligence→Cisco, Protect AI→Palo Alto, Lakera→
Check Point, Invariant→Snyk, etc.). Claims sourced inline.

## 14. Standards posture

**[VERIFIED]**: in-toto Statement v1 certificate layout; Ed25519 signatures.
**[PROPOSED]**: DSSE envelope, Sigstore keyless signing, CycloneDX ML-BOM
import/export, OTel GenAI semantic conventions as the collection layer.

## 15. Deployment & developer instructions

`docs/deployment.md` (compose + local), `README.md` quickstart,
`docs/CONTRIBUTING.md` (gates), `docs/troubleshooting.md`,
`docs/demo-guide.md`.

## 16. Future work

P2: TypeScript SDK; host-level runtime agent (eBPF); Sigstore keyless; replay
nonces; multi-key verification ring; retention enforcement job; DB hash-chained
audit; external red-team of AttackBench; Postgres load testing.

## 17. Remaining risks

1. Fixture/detector co-authorship bias (benchmarks) — external review needed.
2. Small benign-control set → FP rate not yet meaningfully estimated.
3. Compose stack and real-provider paths unverified in this environment.
4. Single-operator bootstrap trust (initial baseline pinning).

## 18. Final audit (independent adversarial review)

A final audit (architect/security/QA/red-team pass over the actual code, with
empirical verification of suspected bugs) produced 21 findings: 2 HIGH,
10 MED, 9 LOW. All HIGH and MED findings were fixed and regression-tested
(`backend/tests/test_audit_fixes.py`, 13 tests); LOW items are tracked in
`docs/agent-state/AUDIT-FINDINGS.md`. Key fixes:

1. **[VERIFIED]** `step.started` no longer double-records steps (was corrupting
   fingerprints and producing wrong UNTRUSTED verdicts for clients following
   the documented vocabulary).
2. **[VERIFIED]** The documented privacy control is now real: payloads are
   recursively sanitized server-side — content keys hashed unless
   `AEGISTRACE_ALLOW_CONTENT=true`; secret-pattern redaction retained.
3. **[VERIFIED]** Withheld-evidence runs can no longer pass silently: pinned
   digests must be attested, expected prompts must be pinned, and allowed_set
   mode flags missing expected steps. (This immediately caught a real gap: the
   demo email tool had never attested its digest.)
4. **[VERIFIED]** Tenant-scoped uniqueness for execution/output ids (no
   cross-tenant id oracle), policy-rule validation (no fail-dead ingestion),
   ingestion audit rows, bounded rate-limiter memory, metrics endpoint admin-
   gated, limits clamped, certificate subject comparison normalized,
   `rerun_of` target validated, replayed finishes idempotent, frontend proxy
   allowlist hardened, benchmark artifacts committed.

## 19. Definition-of-done scorecard

Architecture ✅ · Research ✅ (sourced) · Prior art ✅ (mapped) · Standards ✅ ·
Skills ✅ (`docs/SKILLS.md`) · Backend ✅ · Database ✅ (+migrations) ·
Provenance ✅ · Runtime monitor ✅ (SDK-level; host-level PROPOSED) ·
Fingerprint ✅ · Causal graph ✅ · Trust engine ✅ · Propagation ✅ ·
Output invalidation ✅ · Quarantine ✅ · Recovery ✅ · Certificates ✅ ·
SDK ✅ · Integrations ✅ (stubs-verified; live UNVERIFIED) · MCP ✅ (fixture) ·
RAG ✅ (fixture) · Frontend ✅ (judge-passed) · Graph UI ✅ · Design system ✅ ·
A11y ✅ (contrast/ARIA/keyboard/text-alt) · Responsive ✅ (breakpoints; mobile
nav) · Security ✅ (threat model + tests) · Red team ✅ (AttackBench) ·
Benchmarks ✅ · Comparison ✅ · CI ✅ · Docker ✅ files (run UNVERIFIED) ·
Docs ✅ · Quickstart ✅ · Demo ✅ reproducible · Regression ✅ green ·
No known critical bugs ✅ · No secret leaks ✅ (gitignored keys/data; bootstrap
key is a demo constant).
