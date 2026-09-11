# AegisTrace — White-Space Synthesis

**Status:** Research deliverable (prior-art + standards workstream)
**Date of research:** 2026-09-12
**Claim tags:** `[DOCUMENTED-BY-SOURCE]`, `[OBSERVED]`, `[HYPOTHESIS]`.

> Framing: each white-space hypothesis is ranked, with **evidence for**, **evidence against**, **falsifiers**, and a **minimal experiment** (referencing the project's planned AttackBench + baseline comparisons). These are technical novelty hypotheses — not legal conclusions (see prior-art.md disclaimer).

---

## WS-1 (Rank 1): Expected-vs-Observed execution-graph verification for AI workloads

**Hypothesis:** No shipping product, standard, or published system constructs an *expected* causal graph of an AI/agent execution (model, prompt, retrieval sources, tools, MCP servers, dependencies, runtime) at deploy/policy time, captures the *observed* graph at runtime, and treats **structural/semantic deviation between the two** as the primary security signal. [HYPOTHESIS]

**Evidence FOR:**
- The June 2026 agent-provenance survey lists "unified trace schemas" and standard gaps: "existing standards (W3C PROV-DM, OpenTelemetry, PROV-AGENT) don't fully capture agent-specific semantic and procedural objects" — nobody has a normative *expected* model. [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4]
- PROV-AGENT (closest capture system) covers capture/querying only; abstract lists no deviation detection. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2508.02866]
- Observability vendors verify *content quality*, not *plan conformance*; guardrails verify *content safety*, not *graph conformance*. [HYPOTHESIS grounded in reviewed public materials]
- HOLMES analogizes (compare flows against an expected pattern set = TTPs) but for host attacks, not declared benign AI plans. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/1810.01594]

**Evidence AGAINST:**
- AgentSpec / Progent / CaMeL-style runtime policy enforcement (named by the survey) constrains agent behavior against rules at runtime — a *constrained* execution is close to a *verified* one. If a vendor couples policy enforcement with trace signing, they approximate this. [DOCUMENTED-BY-SOURCE — survey names them; individual papers UNVERIFIED]
- Zenity's "buildtime to runtime" governance language may hide graph-ish internals. [HYPOTHESIS]

**Falsifiers:** a public product/paper demonstrating (a) declarative expected execution graphs for agents, (b) runtime observed-graph capture, (c) automated deviation verdicts — any two of three falsifies the strong form.

**Minimal experiment:** implement expected-graph capture in the SDK for 10 canonical flows; run **AttackBench**'s retrieval-swap / tool-substitution / model-swap attacks; measure deviation-detection precision/recall vs. (i) a Langfuse-trace rule baseline, (ii) a prompt-injection guardrail baseline, (iii) an anomaly-scoring baseline (NoDoze-style path scoring ported to AI semantics). Target: detect graph-level deviations with near-100% recall on structural swaps that content guards miss. [HYPOTHESIS]

---

## WS-2 (Rank 2): Trust propagation over AI causal dependencies with output consequences

**Hypothesis:** No reviewed work propagates trust/compromise states through an AI execution's causal graph and then **quarantines/invalidates/re-certifies the affected outputs** (and downstream artifacts) with cryptographic evidence. [HYPOTHESIS]

**Evidence FOR:**
- The survey explicitly: "systems detect unsafe behavior but rarely use provenance to invalidate stale memory, **quarantine contaminated evidence**, retry, roll back, or request approval." [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4]
- NoDoze/RapSheet prove anomaly-score propagation over causal chains works on hosts; no reviewed work ports it to AI output lifecycle. [DOCUMENTED-BY-SOURCE — https://www.ndss-symposium.org/ndss-paper/nodoze-combatting-threat-alert-fatigue-with-automated-provenance-triage/]
- EU AI Act Art. 12/19 creates a compliance pull for exactly this (automatic event logs, retention, traceability) but no technical standard implements it for AI agents. [DOCUMENTED-BY-SOURCE — https://artificialintelligenceact.eu/article/12/]
- Patent P9 (US20260252995, "revocation controller propagating invalidation events across workloads, sessions, derived artifacts") is adjacent — in a *workload/compute* domain, apparently not AI-output attestation; must be read by counsel. [OBSERVED — abstract only; https://patents.justia.com/patent/20260252995]

**Evidence AGAINST:**
- Memory-contamination work (A-MemGuard, AgentPoison countermeasures) handles *memory* invalidation specifically. [DOCUMENTED-BY-SOURCE — named in survey; details UNVERIFIED]
- Vector DB vendors may ship provenance-aware deletion (post-GDPR "right to be forgotten" engineering) — content-level invalidation without trust semantics. [HYPOTHESIS]

**Falsifiers:** a system that, upon a compromised dependency (e.g., poisoned document, backdoored MCP tool), automatically identifies and cryptographically marks affected past outputs as untrusted — end-to-end.

**Minimal experiment:** AttackBench scenario "poisoned document admitted at T, detected at T+Δ"; measure (a) causal fan-out correctness (which outputs are affected) against ground truth, (b) false-invalidation rate, vs. baseline "nuke the session" and "do nothing" baselines. [HYPOTHESIS]

---

## WS-3 (Rank 3): Verifiable per-execution AI Trust Certificates (signed expected+observed+verdict)

**Hypothesis:** No standard or product issues per-execution, DSSE/in-toto-signed certificates binding expected-graph digest, observed-graph digest, deviation verdict, and trust state — i.e., a *reusable proof of execution trust*. [HYPOTHESIS]

**Evidence FOR:**
- All reviewed attestation standards (SLSA/in-toto/Sigstore) attest **artifacts/steps**, not executions. [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.2/, https://github.com/in-toto/attestation]
- AgentSign (closest community attempt) does signed hash-chains + trust scoring but with hash-only attestation and no causal semantics — and its HN critique ("a prompt-injected agent could sign legitimate-looking malicious instructions, producing a perfect cryptographic audit trail of an attack") defines exactly the gap a graph-based certificate closes. [OBSERVED — https://news.ycombinator.com/item?id=47325206]
- OVERT/TRACE community standards show demand for runtime trust artifacts but define requirements, not certificates. [OBSERVED — https://overt.is/OVERT_v1.1_STANDARD.pdf; TRACE UNVERIFIED]

**Evidence AGAINST:**
- TEE vendors (NVIDIA/Azure/Google) attest execution *environments* strongly; "attested execution" in the TEE sense is a competing interpretation that may satisfy buyers. [DOCUMENTED-BY-SOURCE — https://www.nvidia.com/en-us/data-center/solutions/confidential-computing/]
- Patent space around "LLM attestations" (US20250086270A1) and TEE runtime attestation (US20250259042A1) exists — claim-drafting must steer around them. [OBSERVED — abstracts only]

**Falsifiers:** a published standard (in-toto predicate, OVERT v2, TRACE profile) or product shipping execution-trust certificates with verification tooling.

**Minimal experiment:** define the `execution-trust/v1` predicate (standards.md §16); issue certificates for AttackBench runs; third-party verifier demo (independent service verifies a certificate against a signed trace log) — the "verify without trusting the issuer" property is the demo. [HYPOTHESIS]

---

## WS-4 (Rank 4): Dependency-coverage metrics & benchmarks for agent provenance

**Hypothesis:** The field lacks agreed metrics/benchmarks for execution provenance (trace completeness, provenance accuracy, dependency coverage, temporal consistency) — the survey calls these only "Proposed desiderata" — and AegisTrace can define them via AttackBench. [HYPOTHESIS grounded in a DOCUMENTED-BY-SOURCE statement]

**Evidence FOR:** survey: "No benchmark family provides strong end-to-end coverage"; execution-provenance metrics have "no agreed definitions." [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4]. Who&When covers only failure attribution accuracy (53.5% SOTA). [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2505.00212]

**Evidence AGAINST:** metrics work is cheap to replicate; the survey authors or the AgentTrace/AgenTracer groups may publish first. [HYPOTHESIS]

**Falsifiers:** a published benchmark suite covering evidence+tools+memory+multi-agent+invalidation end-to-end.

**Minimal experiment:** publish AttackBench spec with the four metric definitions and baseline numbers from WS-1/WS-2 experiments; get it cited/adopted. [HYPOTHESIS]

---

## WS-5 (Rank 5): AI-native PIDS (provenance-graph IDS re-targeted from syscalls to AI semantics)

**Hypothesis:** The 2019–2025 PIDS corpus (HOLMES/NoDoze/RapSheet/KAIROS/MORSE/TAPAS) has never been re-targeted to AI execution semantics in a deployed system. [HYPOTHESIS]

**Evidence FOR:** the survey's reviewed systems are all either host-level (PIDS) or semantic-but-enforcement-level (guardrails/IFC); the bridge (PIDS on AI semantics) is empty. [HYPOTHESIS from D sources]; the CCS 2023 industrial study documents why host PIDS stalled — semantic gap + data volume — which AI-level graphs partially *avoid* (fewer, richer events). [DOCUMENTED-BY-SOURCE — https://xusheng-xiao.github.io/papers/provenance_study_ccs_2023.pdf]

**Evidence AGAINST:** OmniSec (LLM-assisted PIDS) shows researchers are actively fusing the fields (wrong direction, but the fusion is happening). [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2503.03108v2]; NEC's granted patent (US11423146B2) covers path-embedding anomaly detection with automated response — broad claims may read on some AI-graph anomaly scoring (counsel check). [OBSERVED]

**Falsifiers:** a published/deployed system running PIDS-style detection over agent-execution graphs.

**Minimal experiment:** port NoDoze's anomaly-score propagation to AegisTrace graph edges; compare against WS-1's declarative expected-graph detector on the same AttackBench corpus (pure anomaly vs. expected-vs-observed — this comparison is itself publishable). [HYPOTHESIS]

---

## Ranked summary

| Rank | White space | Strongest evidence | Biggest threat |
|---|---|---|---|
| 1 | Expected-vs-observed graph verification | Survey gap naming (no normative expected model) [D] | Runtime-enforcement papers (CaMeL/AgentSpec family) |
| 2 | Trust propagation → output quarantine/invalidation/re-certification | Survey: recovery/invalidation named as open gap [D] | Patent P9 adjacency; vector-DB deletion features |
| 3 | Signed per-execution AI Trust Certificates | Attestation standards stop at artifacts [D] | AgentSign-style filings; TEE "attested execution" marketing |
| 4 | Provenance metrics & AttackBench | Survey: metrics are "Proposed" only [D] | Academic groups publishing first |
| 5 | AI-native PIDS | 2023 industrial study shows host-PIDS stall [D] | NEC patent breadth; OmniSec-direction fusion |

## What would kill the whole thesis (meta-falsifiers)

1. Observability vendors add signing + expected-graph comparison (they own distribution). Watch OTEL GenAI semconv maturity and Langfuse/Phoenix roadmaps quarterly. [HYPOTHESIS]
2. TEE + confidential-AI marketing convinces buyers that hardware attestation suffices ("the GPU was attested, therefore the execution is trusted") — AegisTrace must keep demonstrating behavior deviations *inside* attested environments (possible: a TEE-protected run can still call a poisoned MCP server). [HYPOTHESIS; TEE behavior gap is a technical argument, demonstrate it in AttackBench]
3. The white space closes academically before commercially — the survey (Jun 2026) signals the field is 6–12 months from system papers. [HYPOTHESIS]
