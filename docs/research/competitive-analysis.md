# AegisTrace — Competitive Analysis

**Status:** Research deliverable (prior-art + standards workstream)
**Date of research:** 2026-09-12
**Claim tags:** `[DOCUMENTED-BY-SOURCE]`, `[OBSERVED]`, `[HYPOTHESIS]`. Fairness rule: each section first states what the category genuinely already does.

**AegisTrace's thesis questions (the yardstick):**
1. **Q1 — Which trusted components caused THIS output?** (causal attribution per execution)
2. **Q2 — Did the path deviate?** (expected vs. observed execution graph)
3. **Q3 — Can we causally prove output trust?** (trust propagation + signed, per-execution certificate; quarantine/invalidation/re-certification of affected outputs)

---

## 1. SBOM-only tooling (Syft/Grype/Trivy/Anchore-style; SPDX & CycloneDX ecosystems)

**What they genuinely cover** [DOCUMENTED-BY-SOURCE — https://cyclonedx.org/capabilities/mlbom/, https://fossa.com/blog/spdx-3-0/]:
- Complete inventories of components, incl. **models and datasets** via CycloneDX ML-BOM (modelCard, data, algorithmic components) and SPDX 3.0 AI/Dataset profiles; vulnerability matching; license/compliance reporting. This is valuable and AegisTrace should consume it, not rebuild it.

**What they CANNOT answer (for AegisTrace's questions):**
- Q1: an SBOM has **no runtime instantiation** — it cannot tell you which SBOM entry influenced a *specific* output; there is no per-output graph. [HYPOTHESIS]
- Q2: no concept of an execution path, therefore no deviation. An SBOM can be perfectly "clean" while a retrieval poisoned the context at runtime. [HYPOTHESIS]
- Q3: no trust propagation across dependency changes *after deployment* (e.g., "the embedding model you retrieved with was yanked/compromised yesterday — which of the last 24h outputs are invalid?"). [HYPOTHESIS]

**Catch-up path for them:** join SBOM records with per-request telemetry, build runtime bindings of components→executions, add expected/observed comparison and signing. Effectively: build AegisTrace's runtime layer on top. [HYPOTHESIS]

**Positioning:** AegisTrace = "the SBOM's runtime counterpart." SBOM = what could be involved; AegisTrace = what actually was, and whether it behaved. [HYPOTHESIS]

---

## 2. SLSA / in-toto / Sigstore build-attestation stacks

**What they genuinely cover** [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.2/, https://github.com/in-toto/attestation, https://docs.sigstore.dev/cosign/signing/overview/]:
- Hardened builds with verifiable provenance (Build L1–L3), standardized attestation statements (in-toto), keyless signing with transparency logs (Fulcio/Rekor). Mature, widely deployed, and AegisTrace reuses all of it (see standards.md §16).
- Witness/TestifySec already sells "signed, audit-ready evidence" mapped to NIST 800-53/FedRAMP/SOC 2 — proof the attestation-evidence market exists. [DOCUMENTED-BY-SOURCE — https://www.testifysec.com/]

**What they CANNOT answer:**
- Q1: their subject is an **artifact**, not an **execution/output**. "Which components caused this answer?" is out of scope by design. [HYPOTHESIS]
- Q2: they verify **what was built**, not **how a running system behaved**. A perfectly attested model + tool container can still be driven off-script by a prompt injection at inference. [HYPOTHESIS]
- Q3: no runtime trust graph; a compromise discovered post-deployment triggers no invalidation of past results, because past *executions* were never attested — only artifacts. [HYPOTHESIS]

**Catch-up path:** define new in-toto predicates for executions (AegisTrace already proposes this in standards.md), add runtime capture (SDK/OTEL), and trust propagation. That is AegisTrace; the incumbents' institutions (OpenSSF) could standardize it eventually — an argument for contributing the predicate upstream early. [HYPOTHESIS]

---

## 3. Traditional runtime monitoring / eBPF (Falco, Tetragon, Tracee)

**What they genuinely cover:**
- High-fidelity host observability and enforcement from syscalls/eBPF: file/process/socket events, policy enforcement, rule-based detection. Proven, production-grade, CNCF-adjacent. [Well-established; specific doc pages not re-verified this session — UNVERIFIED this session, uncontroversial.]

**What they CANNOT answer:**
- Q1: they see `python connect()`, `open()`, `execve()` — not "the agent used the finance MCP tool with document X retrieved from vector store Y." The semantic gap between syscalls and AI decisions is where attribution dies. [HYPOTHESIS]
- Q2: their "expected vs. observed" is syscall rules (Falco rules), not a *declared causal execution graph* with semantic dependencies. [HYPOTHESIS]
- Q3: no notion of model/prompt/retrieval trust, no certificates over outputs, no invalidation of generated content. A Tetragon policy can kill a process; it cannot tell you which agent answers are now untrustworthy. [HYPOTHESIS]

**Genuine prior art to respect:** the provenance-graph PIDS lineage (HOLMES/NoDoze/RapSheet — see prior-art.md) did for *hosts* what AegisTrace does for *AI executions*; and the CCS 2023 industrial study shows why it struggled (scale/fidelity) — AegisTrace inherits those engineering risks. [DOCUMENTED-BY-SOURCE — https://xusheng-xiao.github.io/papers/provenance_study_ccs_2023.pdf]

**Catch-up path:** instrument AI-framework layers (they can't get semantics from syscalls alone); that's a new product, not an upgrade — genuine moat window. [HYPOTHESIS]

---

## 4. AI observability (LangSmith, Langfuse, Arize Phoenix, W&B Weave; MLflow)

**What they genuinely cover** [DOCUMENTED-BY-SOURCE — license/scope details: https://langfuse.com/resources/engineering/best-phoenix-arize-alternatives, https://arize.com/docs/phoenix/self-hosting/license, https://mlflow.org/arize-phoenix-alternative]:
- First-class LLM/agent tracing: spans for chains, tool calls, retrievals, agent steps; evals; datasets; prompt management; OTEL-native options (Phoenix; OTEL GenAI semconv adoption). **This is 70% of AegisTrace's raw observation layer.** Langfuse is MIT, Phoenix is ELv2, LangSmith closed-source, Weave SDK Apache-2.0/platform commercial, MLflow Apache-2.0. [DOCUMENTED-BY-SOURCE]
- Failure attribution research is appearing around this stack (Who&When, ICML 2025 — attribution over agent logs). [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2505.00212]

**What they CANNOT answer:**
- Q1: traces can answer "what happened" manually; they are **not structured as a causal graph with integrity**, not signed, and not designed to answer "which components *caused* this output" mechanically or verifiably. [HYPOTHESIS]
- Q2: "deviation" in observability = eval scores/drift metrics on *content quality*, not "the execution graph differed from the declared/attested plan" (e.g., an unexpected tool call chain, an unauthorized retrieval source, a swapped model version mid-run). [HYPOTHESIS]
- Q3: nothing is attested; nothing propagates trust; a compromised dependency found tomorrow invalidates nothing — no signed evidence exists to reason over. [HYPOTHESIS]

**Catch-up path:** they already have the telemetry; they would need to add (a) graph assembly + expected-graph model, (b) trust propagation engine, (c) DSSE/in-toto certificate issuance, (d) invalidation/quarantine workflows. (a)–(d) are security-engineering features outside their charter — but their *distribution* (adoption by every AI team) is their catch-up advantage. [HYPOTHESIS]

**Positioning:** partner/integrate (emit AegisTrust certificates from Langfuse/Phoenix traces) rather than compete on tracing. [HYPOTHESIS]

---

## 5. AI guardrail / security vendors (Lakera, Prompt Security, Lasso, Protect AI/Prisma AIRS, HiddenLayer, Robust Intelligence→Cisco AI Defense, CalypsoAI, Knostic)

**What they genuinely cover** [DOCUMENTED-BY-SOURCE — acquisition/press links in ecosystem.md §5]:
- Content-level guardrails (prompt injection, jailbreaks, PII, toxicity), red-teaming, model-file scanning (HiddenLayer/Protect AI scanning), data-need-to-know (Knostic), API/gateway-level policy (Lasso), lifecycle scanning + LLM security + red teaming (Prisma AIRS), end-to-end AI protection (Cisco AI Defense). Real products, real customers, now inside Cisco/PANW/Check Point/SentinelOne/F5/Cato/CrowdStrike. [DOCUMENTED-BY-SOURCE]
- Prompt Security's market map tracks 406 companies — this category is crowded and consolidating fast. [DOCUMENTED-BY-SOURCE — https://prompt.security/ai-security-startup-map]

**What they CANNOT answer:**
- Q1: guards make **per-request content verdicts**; they do not maintain a causal graph over an execution, so "which trusted components caused this output" has no substrate. [HYPOTHESIS]
- Q2: their runtime checks are content/behavior heuristics on the *current* request/response — not comparison against a *declared expected execution graph* (wrong tool called is caught only if it trips a rule; a subtly altered retrieval chain is invisible). [HYPOTHESIS]
- Q3: no propagation, no invalidation: if a dependency is later found compromised, guards have no record linking it to past outputs; nothing is re-certifiable. No reviewed vendor publishes signed execution evidence. [HYPOTHESIS — based on public materials reviewed; re-check quarterly]

**Catch-up path:** they must add a provenance data model + expected-graph verification + certificate signing. Their enterprise channels and telemetry volume make them the most dangerous future competitors; the 2024–2026 acquisition wave shows they buy rather than build — possible acquirer channel for AegisTrace. [HYPOTHESIS]

---

## 6. Agent-tracing security (Invariant Labs → Snyk, mcp-scan/agent-scan; Zenity; Aim → Cato)

**What they genuinely cover:**
- Static + shallow-dynamic scanning of agent setups: MCP servers, tool descriptions, prompt-injection/tool-poisoning patterns, secrets (mcp-scan → snyk/agent-scan "discover and scan agent components… agents, MCP servers, skills"). [O — https://github.com/snyk/agent-scan; D — https://invariantlabs.ai/blog]
- Trace analysis UIs (Invariant Explorer) for reviewing agent trajectories. [D — Invariant product coverage in ecosystem.md]
- Agent-inventory/governance "buildtime to runtime" (Zenity). [D — https://zenity.io/]
- Deep agent-attack research (Invariant found MCP exfiltration issues; tool-poisoning research). [D — acquisition coverage]

**What they CANNOT answer:**
- Q1: scanners enumerate components; traces are *retrospective*. Neither binds "component → this specific output" with integrity. [HYPOTHESIS]
- Q2: they detect *known-bad patterns* in configs/traffic; deviation from a *declared good plan* (expected graph) is a different detection model. [HYPOTHESIS]
- Q3: no trust propagation or output invalidation; scanning is point-in-time. Nothing reviewed issues signed per-execution certificates. [HYPOTHESIS]

**Catch-up path:** scanning vendors would need runtime capture + graph + attestation. Snyk's agent-scan shows they are moving from MCP-only to "agents, MCP servers, skills" — watch for trace-verification features. [O — repo description]

---

## 7. The wildcard category: community standards & adjacent projects

- **AgentSign** (execution-chain signing + hash attestation + trust scoring; "patent pending") — the closest community project to AegisTrace's thesis; its limitations (hash-only attestation; no behavioral deviation; HN criticism: "signatures prove what was sent, not that the signer wasn't compromised") are AegisTrace's differentiation map. [O — https://news.ycombinator.com/item?id=47325206]
- **OVERT / TRACE standards** — runtime-trust requirements for AI incl. MCP attestation; validation of demand; potential integration targets. [O — https://overt.is/OVERT_v1.1_STANDARD.pdf; TRACE UNVERIFIED]
- **PROV-AGENT / NeuroTaint (academia)** — capture/query (PROV-AGENT) and taint tracking (NeuroTaint); neither does expected-vs-observed verification + certificates + invalidation per their public descriptions. [D — prior-art.md §2]

---

## 8. Summary matrix

| Category | Q1: which components caused THIS output? | Q2: did the path deviate (expected vs observed)? | Q3: causally provable output trust (certs, invalidation)? |
|---|---|---|---|
| SBOM-only | No — static inventory [H] | No [H] | No [H] |
| SLSA/in-toto/Sigstore | No — artifact subjects [H] | No — build-time only [H] | Artifacts only; no runtime certs [H] |
| eBPF runtime (Falco/Tetragon/Tracee) | Not at AI semantics [H] | Rules ≠ expected graph [H] | No [H] |
| AI observability | Manual reading of traces only [H] | Quality/eval drift ≠ graph deviation [H] | Unsigned, unattested traces [H] |
| Guardrail/security vendors | No — per-request verdicts [H] | Content heuristics only [H] | No propagation/invalidation [H] |
| Agent-tracing security | Config/scan-level only [H] | Known-bad patterns only [H] | No [H] |
| **AegisTrace** | **Yes — causal graph per execution [design goal]** | **Yes — expected vs observed graphs [design goal]** | **Yes — signed trust certificates + quarantine/invalidation/re-certification [design goal]** |

(“[H]” = [HYPOTHESIS]: claims about what competitors cannot do are based on reviewed public materials and the categories' published scopes; vendors' private capabilities may differ — re-validate before any public competitive claim.)

## 9. Fairness notes (where competitors genuinely lead)

- **Observability vendors** already own the telemetry pipelines and developer mindshare AegisTrace needs; integration-first is the only sane GTM. [HYPOTHESIS]
- **SLSA/in-toto/Sigstore** are standards with institutional momentum; AegisTrace must ride them (custom predicate, keyless signing), never fork them. [HYPOTHESIS]
- **Guardrail vendors** excel at content-level threats (prompt injection detection) where AegisTrace is intentionally weak; AegisTrace answers *systemic/trust* questions they don't. Complementary sale. [HYPOTHESIS]
- **eBPF/PIDS research** solved hard scaling problems (MORSE compression, TAPAS online detection) that AegisTrace will hit; reuse their techniques. [DOCUMENTED-BY-SOURCE — https://www.ndss-symposium.org/wp-content/uploads/2025-822-paper.pdf, https://www.usenix.org/conference/usenixsecurity25/presentation/zhang-bo-tapas]
