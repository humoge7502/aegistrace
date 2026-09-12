# AegisTrace — Threat Model

_Status: v1.0 (2026-09-12). Method: STRIDE-per-element over the four planes of
`docs/architecture/architecture.md`, plus AI-specific abuse cases. Classification:
[D] designed/mitigated, [P] partially mitigated, [F] future work, [O] out of scope._

## 1. Assets

1. Provenance graph + raw events (tamper → false trust conclusions).
2. AI Trust Certificates and the signing key (forge → false trust claims).
3. Trust states / decisions (flip → suppress or fake incidents).
4. API keys (impersonation, cross-tenant access).
5. Customer metadata captured by the SDK (confidentiality).
6. Availability of the ingestion path (block → blind the attestation).

## 2. STRIDE by plane

### Agent plane (SDK in customer process)

| Threat | Vector | Class | Status |
|---|---|---|---|
| SDK bypassed by attacker | malicious code runs without `@trace` | S/T | [P] — baselines catch steps that appear (unexpected_component); steps never emitted → missing evidence → UNKNOWN. Mitigation: runtime step-level collection is a documented gap; see §5 |
| Compromised collector process | attacker controls SDK host | C/E | [P] — attacker can emit forged "trusted" events; mitigated by server-side expected-state comparison (they must also forge matching digests/path) and by signature keys never residing client-side. Fully trusted clients are [O] for v1 — see honest-limitations |
| Secret leakage through events | prompts/args contain credentials | I | [D] — hash-by-default; secret-pattern redaction on metadata; backend re-sanitizes |

### Ingestion plane

| Threat | Vector | Class | Status |
|---|---|---|---|
| Event forgery / replay | stolen agent key | S | [P] — keys are scoped+hashed; replay of `execution.started` dedupes; replay of full runs is detectable via duplicate fingerprints (documented; per-event nonce [F]) |
| Injection via payloads | crafted JSON | T | [D] — Pydantic validation, parameterized SQL (ORM), no unsafe deserialization |
| Denial of ingestion | flood | D | [P] — per-key token bucket (single-instance); distributed limits [F] |
| Tenant boundary crossing | key misuse | I/E | [D] — every query tenant-scoped; isolation tests enforced in CI |

### Graph/trust plane

| Threat | Vector | Class | Status |
|---|---|---|---|
| DB tampering to flip trust | insider/SQL access | T/E | [P] — certificates are signed server-side; flipping trust states does not forge certificates; DB-level tampering detection (hash chains) [F] |
| Certificate forgery | steal signing key | F | [P] — key stored with 0600 outside VCS; key rotation endpoint [F]; HSM/KMS [F]; Sigstore keyless [F] |
| Propagation evasion | re-register component under new name | E | [P] — digest pinning is name-scoped; aliasing is visible in graph; namespace governance [F] |
| Policy weakening by insider | admin edits policy to always-trust | S | [P] — policy changes audit-logged with actor; policy approvals workflow [F] |

### Interface plane

| Threat | Vector | Class | Status |
|---|---|---|---|
| UI redressing of evidence | misleading graph rendering | R | [P] — evidence JSON viewer shows raw signed statements; certificate verify button re-checks server-side |
| API abuse | enumeration of ids | I | [D] — UUIDs, tenant scoping, RBAC, rate limits |

## 3. AI-specific abuse cases (mapped to AttackBench)

| Abuse case | AttackBench scenario | Detection |
|---|---|---|
| Model artifact tampering | model-tampering | digest_mismatch (critical) |
| Prompt injection changing system prompt | prompt-tampering | prompt_mismatch (critical) |
| Corpus/dataset poisoning | dataset-poisoning, rag-poisoning | digest_mismatch / unexpected_component |
| Malicious dependency substitution | dependency-substitution | digest_mismatch |
| Container/image tampering | container-modification | digest_mismatch |
| Tool compromise | tool-compromise | digest_mismatch |
| MCP server compromise | mcp-compromise | digest_mismatch |
| Runtime manipulation | runtime-manipulation | unexpected_component |
| Execution-path deviation (normal output) | path-deviation | path_deviation + unexpected_component |
| Multi-component attack | multi-component | both |
| Forged attestation | forged-attestation | signature verification fails |
| Blind the collector | stale-trust | missing_provenance → UNKNOWN |
| Post-hoc dependency compromise | historical-dependency-compromise | propagation → outputs invalidated + certs revoked |

## 4. Privacy threats

| Threat | Mitigation |
|---|---|
| Prompts/documents exfiltrated via events | hash-by-default (ADR-005); content opt-in per step; backend rejects/hashes raw content keys when `AEGISTRACE_ALLOW_CONTENT=false` |
| Over-collection | SDK captures identity/digests/timing only by default |
| Retention abuse | `AEGISTRACE_RETENTION_DAYS` documented; retention enforcement job [F] |

## 5. Honest limitations (what this system cannot do today)

1. A fully compromised *client host* can lie about what it executes: server-side
   expected-state comparison raises the bar (attacker must also match pinned
   digests and path), but cryptographically attesting *what ran on the host*
   requires TEE/measured-boot integration — [F].
2. Digest pinning depends on trustworthy expected values at registration time
   (tofu-style); initial baseline provisioning needs governance.
3. Single-instance rate limiting and metrics; horizontal deployments need a
   shared limiter and OTel export — [F].
4. Log/DB tamper-evidence (hash-chained audit trail) — [F].

## 6. Red-team cadence

AttackBench (`benchmarks/attackbench/`) runs the abuse-case matrix above in CI;
any scenario regression fails the build. New abuse cases must ship with a
fixture and an expected-detection contract.
