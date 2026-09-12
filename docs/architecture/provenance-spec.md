# AegisTrace Provenance Specification v1

_Machine-readable event vocabulary and entity contract (v1, stable)._
_Companion: `docs/architecture/api.md` (transport), `docs/architecture/trust-model.md` (semantics)._

## 1. Entities

| Entity | Identity | Key fields |
|---|---|---|
| Component | tenant + kind + name + version (unique) | `digest_expected`, `digest_observed`, `trust_state`, `meta` |
| Baseline | tenant + agent_ref (latest active) | `mode` (sequence/allowed_set/policy_only), `doc`: steps, allowed sets, `component_digests`, `prompt_hashes` |
| Execution | tenant + `external_id` (SDK run id, unique) | `agent_ref`, `baseline_id`, ordered `steps`, `fingerprint`, `trust_state` |
| Output | tenant + `external_id` | `digest` (sha256 of content), `trust_state`, `quarantined` |
| Edge | typed (src_kind, src_id) → (dst_kind, dst_id) | `kind` (step/produced/depends_on), `seq`, `expected`, `ts`, `execution_id` |
| IntegrityEvent | uuid | `kind`, `severity`, `expected`, `observed`, `evidence` |
| TrustDecision | uuid | `subject`, `state`, `reason`, `evidence` (hop chains, event ids, policy) |
| Certificate | `ATC-<hex>` serial | in-toto statement + Ed25519 signature + status |

## 2. Event vocabulary (SDK → `POST /api/v1/events/batch`)

Envelope: `{ kind, execution_external_id, ts?, payload }`.

| kind | payload fields | effects |
|---|---|---|
| `execution.started` | `agent_ref`, `agent_version?`, `rerun_of?` | creates Execution; binds latest active Baseline; pre-registers expected components |
| `prompt.pinned` | `role`, `hash` | stores into execution prompt_hashes (baseline comparison) |
| `step.ended` | `seq`, `kind` (model/retrieval/tool/mcp/api/embedding/runtime/package/custom), `target`, `digest?`, `meta?`, `version?` | upserts Component; appends ordered step; adds causal edge `execution -step→ component` |
| `component.observed` | `kind`, `name`, `version?`, `digest?`, `meta?` | attests component state (outside or inside a run) |
| `output.produced` | `digest`, `output_kind?`, `output_id?` | creates Output + edge `execution -produced→ output` |
| `execution.finished` | `status` (completed/failed) | freezes fingerprint; baseline comparison → IntegrityEvents → TrustDecision → policy actions → certificate |

Rules: events apply transactionally per batch; `execution.started` is idempotent
(dedup by external id); steps before `started` are rejected 422; each event is
flushed before the next is processed (fresh sessions see committed-in-transaction state).

## 3. Fingerprints

Execution fingerprint = `sha256(canonical_json([{kind,target,digest}...] sorted by seq))`.
It is the certificate subject digest. Order changes change the fingerprint; in
`allowed_set` mode a permutation is legitimate (no path_deviation) but still
produces a different fingerprint — documents "same components, different run shape".

## 4. Deviation kinds

`digest_mismatch` (critical) · `unexpected_component` (critical) ·
`path_deviation` (high) · `missing_step` (medium) · `prompt_mismatch` (critical) ·
`missing_provenance` (medium, zero steps → state UNKNOWN).

## 5. Certificate predicate type

`https://aegistrace.dev/attestations/execution-trust/v1` — in-toto Statement v1
(see `docs/architecture/api.md` §Certificate statement format).

## 6. Stability & evolution

v1 is the demo/SDK contract. Planned v2 additions (additive only): event nonces
for replay hardening, `depends_on` component edges, per-step latency/usage
metrics, DSSE envelope encoding, Sigstore keyless signing.
