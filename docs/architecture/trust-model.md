# AegisTrace — Trust Model

_Status: v1.0 (2026-09-12). Companion to `docs/architecture/architecture.md`._

## 1. Philosophy

**UNKNOWN ≠ TRUSTED.** A trust state is a *claim backed by evidence*; the system
never converts absence of evidence into trust. Every state change writes an
explainable `TrustDecision` (state, reason, evidence chain, deciding principal).
There are no opaque scores.

## 2. States

| State | Meaning | Set by |
|---|---|---|
| `TRUSTED` | All baseline checks passed (digests, path, allow-lists, prompts) | trust engine at execution finish |
| `UNTRUSTED` | ≥1 critical/high deviation, or dependency on a compromised component | trust engine / propagation |
| `UNKNOWN` | No baseline registered, or zero provenance evidence | trust engine (default-deny) |
| `DEGRADED` | Medium/low deviations (e.g. missing expected step) | trust engine |
| `COMPROMISED` | Component identified as attacker-controlled (root state) | operator/API or digest evidence |
| `QUARANTINED` | Output isolated from downstream consumption | policy on UNTRUSTED outputs |
| `RECOVERING` | Component restored; re-execution required | recovery action |
| `RE-CERTIFIED` | Re-run of a previously affected execution passed all checks | trust engine (`rerun_of`) |

Transitions are monotone-safe: recovery never silently re-trusts historical
outputs; only explicit re-execution + verification produces `RE-CERTIFIED`.

## 3. Decision inputs

1. Integrity events from expected-vs-observed comparison (severity ranked).
2. Presence of a baseline (`UNKNOWN` if none, under strict default policy).
3. Evidence completeness (zero steps → `UNKNOWN` regardless of deviations).
4. Causal ancestry: current trust state of every component in the execution path.
5. Tenant policy rules (`Policy.rules`, defaults in `policy/engine.py`).

## 4. Propagation semantics

When component C is marked `COMPROMISED` at time T:

```
for each edge (execution E -step→ C)         [scope: all_history | from T]
    E.trust_state          = UNTRUSTED       (+ TrustDecision, chain hop 1)
    for each edge (E -produced→ O)
        O.trust_state      = UNTRUSTED       (+ chain hop 2)
        O.quarantined      = true            (policy quarantine_outputs)
        certificate(E)     = REVOKED         (reason recorded)
    QuarantineAction rows  written per target
Incident created (root=C, evidence=chains, affected lists, revoked serials)
```

Explainability contract: every impacted subject exposes its hop chain
(`component → execution → output`) with the evidence class of each hop —
rendered in the UI and returned by `GET /components/{id}/impact`.

## 5. Certificate validity

A certificate is *valid* iff: (a) Ed25519 signature verifies over the canonical
statement, (b) status is `ACTIVE`, (c) subject digest still equals the
execution's current fingerprint. Revocation is immediate on any propagation
touching the execution; revocation reason is preserved. Certificates are
issued only for completed executions with state `TRUSTED`/`RE-CERTIFIED` and
only when policy `certify_trusted` is enabled.

## 6. Failure posture

| Failure | Behavior |
|---|---|
| Collector/SDK offline mid-run | Execution finishes with missing steps → `UNKNOWN`/`DEGRADED`, never trusted |
| Backend unreachable | SDK buffers events locally (bounded); executions absent server-side are unattested |
| Duplicate events | `execution.started` is idempotent (dedup by external id) |
| Out-of-order events | Steps ordered by `seq`; finish requires prior start |
| Invalid/trusted-less components | `UNKNOWN` at creation; allow-lists gate their use |
| Rollback unavailable | Recovery records `RECOVERING`; re-execution is the only re-certification path — never fabricated |

## 7. Explicit non-goals (v1)

- No confidential-computing/TEE attestation of the runtime hardware (future work).
- No taint tracking of data *content* through transformations (provenance is at
  component/execution granularity).
- No probabilistic anomaly scoring — evidence-based classification only.
