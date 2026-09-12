# Final Audit — Findings Ledger

_Audit date: 2026-09-12. Method: independent adversarial code review with
empirical verification (pipeline reproduction of suspected bugs). 21 findings:
2 HIGH, 10 MED, 9 LOW. All HIGH/MED fixed and regression-tested in
`backend/tests/test_audit_fixes.py` (13 tests). LOW items tracked here._

## HIGH — fixed ✅

1. **step.started/step.ended double-recording** — a client following the
   documented vocabulary got steps recorded twice → corrupted fingerprints and
   wrong UNTRUSTED verdicts. Fix: only `step.ended` records (started stays in
   the raw log). Regression: `test_step_started_does_not_record`.
2. **Privacy control was dead code** — `CONTENT_KEYS`/`allow_content` were
   never enforced; raw content could persist. Fix: recursive server-side
   sanitization (`sanitize_payload`), content keys hashed unless
   `AEGISTRACE_ALLOW_CONTENT=true`. Regressions: `test_content_keys_hashed_by_default`,
   `test_raw_content_rejected_end_to_end`.

## MED — fixed ✅

3. Global-unique external ids → tenant-scoped unique indexes (`ix_executions_tenant_external`,
   `ix_outputs_tenant_external`); migration regenerated; regression added.
4. Empty allow-list meant "allow anything" → now deny-all (missing key = unconstrained).
5. Withheld evidence passed silently → pinned digests must be attested, expected
   prompts must be pinned, allowed_set mode flags missing expected steps.
   (This immediately caught the demo email tool never attesting its digest.)
6. Component trust endpoint accepted arbitrary states un-audited → now only
   COMPROMISED/TRUSTED, everything audited.
7. Ingestion (highest-volume mutation) wrote no audit rows → per-batch audit.
8. Policy PUT accepted arbitrary rules → validated against the policy schema
   (no fail-dead ingestion from a typo).
9. Propagation ignored tenant policy / `from_compromise_time` unusable →
   tenant policy loaded; scope threads a compromise timestamp.
10. Frontend proxy allowlist bypassable (prefix match, dot segments) and lossy
    (query strings dropped) → exact first-segment match, dot-segment rejection,
    search forwarded.
11. Benchmark result files not committed → all four artifacts now in
    `docs/benchmarks/` and committed.
12. Benign-meta-variation fixture was identical to benign-exact; forgery test
    bypassed `verify_certificate` → fixture now varies metadata; forgery goes
    through the shared `verify_statement` core (signature + status + subject),
    and `verify_certificate` delegates to the same core.

## LOW — tracked

13. ✅ FIXED Rate-limiter unbounded per-key memory → capped/evicted (10k buckets).
14. ✅ FIXED `/metrics` unauthenticated + `/readyz` internal-error leak → admin-gated, generic errors.
15. ✅ FIXED `?limit=-1` dumped tables (SQLite negative LIMIT) → clamped ≥0.
16. ✅ FIXED Certificate subject comparison relied on an accidental double clause → normalized strip+compare, empty digests rejected.
17. ✅ FIXED `RE-CERTIFIED` granted on agent-reported `rerun_of` without validation → target must exist in tenant.
18. ✅ FIXED Certificates embedded `tenant: "unknown"` for non-bootstrap tenants → name resolved from DB at issuance.
19. ✅ FIXED Replayed `execution.finished` re-decided and re-issued certificates → idempotent short-circuit.
20. Partially addressed: cross-tenant write regression added; content
    sanitization regressions added; audit test now covers ingestion; operator
    boundary covered by existing viewer/operator tests. Remaining suggestion
    (more RBAC matrix tests) is tracked as future hardening.
21. ✅ FIXED Demo used a well-known admin key constant → random per-run key
    (external mode requires `AEGISTRACE_BOOTSTRAP_KEY`).

## What held up (verified by the audit)

Tenant scoping consistent on every traced query; key storage hashed and
non-recoverable; Ed25519 signing/verification correct over canonical JSON and
the DB-tamper forgery genuinely fails; RBAC role sets match the documented
matrix including ingest-only agent keys; benchmark claims matched committed
artifacts after fix 11.
