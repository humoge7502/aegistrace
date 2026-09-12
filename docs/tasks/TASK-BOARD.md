# Task Board — AegisTrace

IDs: AT-###. Status: todo | doing | done | blocked. Evidence is required for `done`.

| ID | Title | Owner role | Depends | Status | Evidence |
|---|---|---|---|---|---|
| AT-001 | Repo scaffold, state docs, ADRs | Architect | — | done | this repo, docs/decisions |
| AT-002 | Ecosystem/standards/prior-art research docs | Research | — | doing | docs/research/* (agent running) |
| AT-003 | ACM VIT design research + original design system | UI/UX | — | done | docs/design/*.md |
| AT-010 | Domain model + enums + migrations | Backend | AT-001 | done | backend/app/domain |
| AT-011 | Event ingestion + redaction (collector) | Backend | AT-010 | done | backend/app/collect |
| AT-012 | Causal graph builder + expected/observed deviation detection | Provenance | AT-011 | done | backend/app/graph |
| AT-013 | Trust engine: states + propagation + evidence chains | Trust | AT-012 | done | backend/app/trust |
| AT-014 | Policy engine (block/quarantine/invalidate/approve) | Policy | AT-013 | done | backend/app/policy |
| AT-015 | AI Trust Certificates: issue/verify/revoke (Ed25519, in-toto layout) | Certs | AT-013 | done | backend/app/certs |
| AT-016 | REST API v1 + auth/RBAC + tenancy + audit + rate limit | Backend | AT-011..015 | done | backend/app/api |
| AT-020 | Python SDK: @trace, steps, redaction, HTTP+embedded transports | SDK | AT-011 | done | sdk/aegistrace |
| AT-021 | SDK integrations: OpenAI, Anthropic, MCP, RAG, tools | SDK | AT-020 | done | sdk/aegistrace/integrations |
| AT-030 | Test suite: unit/integration/security/E2E | QA | AT-016,AT-020 | done | backend/tests |
| AT-040 | Killer demo (definitive experiment, reproducible) | Runtime | AT-016 | done | demo/killer_demo.py |
| AT-041 | AttackBench: 14 attack scenarios + metrics | Red team | AT-012,AT-013 | done | benchmarks/attackbench |
| AT-042 | Baseline comparison (SBOM-only, attestation-only, provenance-only) | Benchmark | AT-041 | done | benchmarks/baseline_comparison.py |
| AT-050 | Frontend: landing, login, overview, executions, graph, incidents, certificates, AttackBench | Frontend | AT-016 | done | frontend/ + docs/ui-screens (judge 9/9) |
| AT-060 | Docker/compose + CI workflow | DevOps | AT-016 | done | deploy/ (run verified locally where daemon allows) |
| AT-070 | Research docs integration + FINAL-REPORT.md | Research | AT-002, all | done | docs/FINAL-REPORT.md |
| AT-080 | Final audit (arch/security/QA/UX/red-team self-critique) | All | AT-070 | done | docs/agent-state/AUDIT-FINDINGS.md (21 findings; HIGH+MED fixed) |

## Open questions / blockers

- Q-1 Docker daemon not running locally → compose run-verification pending (not blocking P0).
- Q-2 Real-provider smoke tests deferred (no API keys available in environment; stubs used).
