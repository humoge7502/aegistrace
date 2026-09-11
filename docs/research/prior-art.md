# AegisTrace — Technical Prior-Art Mapping

**Status:** Research deliverable (prior-art + standards workstream)
**Date of research:** 2026-09-12
**Claim tags:** `[DOCUMENTED-BY-SOURCE]`, `[OBSERVED]`, `[HYPOTHESIS]`, **UNVERIFIED** where applicable.

> **MANDATORY DISCLAIMER — READ FIRST.** This document is a *technical* prior-art survey assembled from public sources (Google Patents/Justia listings, arXiv, USENIX/NDSS/ACM records, GitHub, vendor pages). It is **NOT legal advice**, and it is **NOT a freedom-to-operate, patentability, invalidity, or infringement analysis**. Claims are summarized from abstracts and secondary descriptions; actual claim scope can only be established by reading full granted claims with a qualified patent attorney. The "white space" sections are **technical novelty hypotheses, not legal conclusions**. Before making any IP decision (filing, publishing, or shipping), engage professional patent counsel.

Each entry follows the structure: **Source | Date | Relevant claims/features | Overlap with AegisTrace | Differences | Possible white space | Confidence | Link.**

---

## 1. Provenance-graph-based intrusion detection & alert triage (the classic prior art)

These systems are the closest *methodological* ancestors of AegisTrace: they build causal provenance graphs from system events, propagate suspicion/trust over them, and turn graph structure into decisions. They operate on **OS-level events** (processes, files, sockets), not AI semantics — but their algorithms (TTP hypothesis graphs, anomaly-score propagation, causal-chain triage) are exactly the machinery AegisTrace re-targets at model/tool/MCP/dependency semantics.

### 1.1 HOLMES — "Real-Time APT Detection through Correlation of Suspicious Information Flows" (IEEE S&P 2019)

- **Source:** Milajerdi, Gjomemo, Eshete, Sekar, Venkatakrishnan (UIC); IEEE Symposium on Security & Privacy 2019; ~968 citations per search-result coverage. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/1810.01594 and https://www.computer.org/csdl/proceedings-article/sp/2019/666000b137/1dlwmkfhv4A]
- **Date:** 2019. **Venue correction:** IEEE S&P 2019 (the project brief said USENIX Security — that is incorrect per sources above). [DOCUMENTED-BY-SOURCE]
- **Technique:** maps suspicious information flows from system audit data onto **MITRE ATT&CK TTPs**, maintaining a **TTP-based hypothesis graph**; produces a real-time detection signal plus a kill-chain visualization of coordinated APT activity. [DOCUMENTED-BY-SOURCE — same links]
- **Overlap with AegisTrace:** HIGH conceptually — "correlate events into a causal graph and interpret it against an expected model (TTPs/kill chain)" is the same *shape* of reasoning as expected-vs-observed execution graphs.
- **Differences:** HOLMES detects *known attacker behavior patterns* in OS event streams; AegisTrace verifies *any deviation of an AI execution from a declared expected graph* and computes output trust. HOLMES has no AI/agent semantics, no certificates, no output invalidation. [HYPOTHESIS]
- **White space:** re-targeting TTP-style hypothesis graphs to agentic AI (prompt-injection TTPs, tool-misuse TTPs) and *attesting* the comparison result. [HYPOTHESIS]
- **Confidence:** HIGH (verified sources). **Link:** https://arxiv.org/abs/1810.01594

### 1.2 NoDoze — "Combatting Threat Alert Fatigue with Automated Provenance Triage" (NDSS 2019)

- **Source:** Hassan, Guo, Li, Chen, Jee, Li, Bates (UIUC/UT Dallas); NDSS 2019. [DOCUMENTED-BY-SOURCE — https://www.ndss-symposium.org/ndss-paper/nodoze-combatting-threat-alert-fatigue-with-automated-provenance-triage/ and https://par.nsf.gov/servlets/purl/10085663]
- **Technique:** for each IDS alert, generates a **causal provenance graph**, **anomaly-scores information-flow paths**, and aggregates the top-k most suspicious paths into an overall alert score — i.e., **score propagation along causal chains** for automatic triage. [DOCUMENTED-BY-SOURCE — same links; ~650 citations per search coverage]
- **Overlap with AegisTrace:** HIGH — this is the direct ancestor of AegisTrace's "trust propagation through causal dependencies." NoDoze propagates *anomaly scores* over causal edges; AegisTrace propagates *trust/compromise* over agent execution graphs.
- **Differences:** NoDoze triages *alerts on hosts*; AegisTrace decides the fate of *AI outputs* (quarantine/invalidate/re-certify) and produces signed evidence. NoDoze scores are relative to historical baselines, not a declared expected graph. [HYPOTHESIS]
- **White space:** bidirectional trust propagation over *semantic* AI dependencies (retrieval → model → tool → output), plus certificate issuance as the triage output. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://www.ndss-symposium.org/ndss-paper/nodoze-combatting-threat-alert-fatigue-with-automated-provenance-triage/

### 1.3 RapSheet — "Tactical Provenance Analysis for Endpoint Detection and Response Systems" (IEEE S&P 2020)

- **Source:** Hassan, Bates, Marino, Katsaros, Agrawal, Gupta (UIUC + Symantec); IEEE S&P 2020; evaluated with Symantec EDR in an enterprise environment; consistently ranked truly malicious TPGs higher. [DOCUMENTED-BY-SOURCE — https://dartlab.org/assets/pdf/rapsheet.pdf]
- **Venue correction:** IEEE S&P 2020 (brief said CCS — incorrect per source). [DOCUMENTED-BY-SOURCE]
- **Technique:** **Tactical Provenance Graphs (TPGs)** — combines low-level system events with **high-level EDR detection logic** to triage EDR alerts; the paper notes its IIP-graph approach is what distinguishes it from NoDoze's path-based triage and HOLMES's full-pattern matching. [DOCUMENTED-BY-SOURCE — same PDF]
- **Overlap:** HIGH — RapSheet's insight ("combine raw provenance with *high-level detection logic*") anticipates AegisTrace's "combine raw AI traces with *declared expected graphs*."
- **Differences:** endpoint focus, alert triage only, no artifact/invalidation semantics, no AI. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://dartlab.org/assets/pdf/rapsheet.pdf

### 1.4 KAIROS — "Practical Intrusion Detection and Investigation using Whole-System Provenance" (CCS 2022)

- **Source:** Hassan, Guo, Li, Chen, Lee, Vij, Stoeckert, Jee, Chen, Bates; CCS 2022. arXiv version: "Kairos: Practical Intrusion Detection and Investigation Using Whole-System Provenance" [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2308.05034v3]
- **Technique:** deep graph learning + **community detection** on sparse whole-system provenance graphs for anomaly-based IDS and attack investigation. [DOCUMENTED-BY-SOURCE — same link]
- **Overlap:** MEDIUM — graph-learning-based anomaly detection over causal graphs; AegisTrace's rule/declarative expected-graph comparison is a different (more auditable) mechanism, but KAIROS is a natural baseline in AttackBench.
- **Differences:** unsupervised anomaly detection; no expected-graph semantics, no trust certificates. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://arxiv.org/html/2308.05034v3

### 1.5 MORSE — rule-based streaming provenance compression

- **Source:** MORSE is described in the literature as a **memory-efficient online provenance compression** system for APT detection (rule-based, with tag attenuation), cited alongside SLEUTH and HOLMES as leading rule-based PIDS. [DOCUMENTED-BY-SOURCE — https://dl.acm.org/doi/full/10.1145/3539605 (survey) and https://www.ndss-symposium.org/wp-content/uploads/2025-822-paper.pdf (CAPTAIN, NDSS 2025, which reimplements MORSE as a baseline)]
- **Venue:** frequently cited as RAID 2023 — **UNVERIFIED this session**; cite by content, not venue, until confirmed.
- **Overlap:** MEDIUM — its **lossless-enough causal compression** solves the scalability problem AegisTrace will hit at high event rates.
- **Differences:** compression/detection of host attacks; no AI semantics. [HYPOTHESIS]
- **Confidence:** MEDIUM-HIGH (existence/technique verified via survey + CAPTAIN PDF; venue unconfirmed). **Links:** https://dl.acm.org/doi/full/10.1145/3539605

### 1.6 FlashGuard — (correction: ransomware-tolerant storage, CCS 2017)

- **Source:** "FlashGuard: Leveraging Intrinsic Flash Properties to Defend Against Encryption Ransomware," Huang et al., **CCS 2017** — an append-only-flash **recovery** system for ransomware, **not** a provenance-based APT detector. [DOCUMENTED-BY-SOURCE — https://jianh.web.engr.illinois.edu/papers/flashguard-ccs17-jian.pdf]
- **Relevance:** weak; only the *recovery from confirmed compromise* theme rhymes with AegisTrace's output invalidation/re-certification. A different, provenance-flavored "FlashGuard" reference appeared in a data-storage-lab listing (NDSS'21) that we could **not** resolve — treat the NDSS'21 FlashGuard attribution as **UNVERIFIED**. [OBSERVED ambiguity — https://github.com/data-storage-lab/Security]
- **Confidence:** HIGH that CCS'17 FlashGuard is storage recovery; LOW relevance.

### 1.7 ProPatrol

- **Status:** **UNVERIFIED this session.** Targeted searches ("ProPatrol provenance APT attack detection USENIX") returned no direct hits. A paper "ProPatrol: Attack Investigation using Pervasive Information Gathering Between Hosts" exists in this author's prior knowledge (provenance-based, attack-recovery oriented) but could not be confirmed with a live source today — **do not cite externally until verified.** [UNVERIFIED]

### 1.8 Classics: BackTracker, SITAR/PASIS, Wang & Stolfo lineage

- **BackTracker** (King & Chen, OSDI 2003): backward/forward analysis from infection points through OS audit logs — the founding "lineage" system of this field. [HYPOTHESIS from domain knowledge; canonical citation exists but was not fetched this session — verify before external use. **UNVERIFIED this session.**]
- **SITAR** ("A Scalable Intrusion Tolerant Architecture," ~2001) and **PASIS** (CMU self-healing storage): early intrusion-tolerance/recovery systems that inspired "detect → contain → re-certify" thinking. [HYPOTHESIS / **UNVERIFIED this session** — the user brief's attribution of these as provenance-lineage work is loose; treat as background.]
- **Wang & Stolfo lineage:** anomaly detection over program/system behavior (e.g., file-anomaly detection) — the *host-side* ancestor of anomaly-scoring approaches like NoDoze. [HYPOTHESIS / **UNVERIFIED this session**.]
- **Modern survey anchor:** "Provenance-based Intrusion Detection Systems: A Survey" (ACM Computing Surveys, 2022, Zipperle et al., ~228 citations) — use this as the canonical map of the PIDS field. [DOCUMENTED-BY-SOURCE — https://dl.acm.org/doi/full/10.1145/3539605]
- **Industrial reality-check:** "Are we there yet? An Industrial Viewpoint on Provenance-based Intrusion Detection" (CCS 2023, Dong et al.) documents why PIDS hasn't fully shipped: data volumes, fidelity, deployment cost — a *risk register* AegisTrace inherits. [DOCUMENTED-BY-SOURCE — https://xusheng-xiao.github.io/papers/provenance_study_ccs_2023.pdf]

### 1.9 Adjacent modern systems (for AttackBench baselines)

- **FLASH** (provenance-graph GNN IDS, ~256 citations): https://dartlab.org/assets/pdf/flash.pdf [D]
- **SLEUTH** (USENIX Security 2020, tag-based forward tracking; surfaced in search coverage) [D via coverage]
- **Unicorn** (graph sketching anomaly detection) [D via coverage of the same lineage]
- **MAGIC** (masked graph autoencoders, USENIX Security 2024): https://www.usenix.org/conference/usenixsecurity24/presentation/jia-zian [D]
- **TAPAS** (efficient online APT detection, USENIX Security 2025): https://www.usenix.org/conference/usenixsecurity25/presentation/zhang-bo-tapas [D]
- **Slot** (graph RL, arXiv:2410.17910): https://arxiv.org/html/2410.17910v3 [D]
- **CAPTAIN** (NDSS 2025, lightweight adaptive PIDS): https://www.ndss-symposium.org/wp-content/uploads/2025-822-paper.pdf [D]
- **OmniSec** (LLM-assisted PIDS, arXiv:2503.03108): https://arxiv.org/html/2503.03108v2 [D] — *inbound* direction (LLMs helping PIDS), not PIDS for agents.

---

## 2. Data-flow / taint provenance for LLM pipelines (2024–2026)

The field is young and moving fast; the June 2026 survey is the best map. Key entries verified this session:

### 2.1 Survey: "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents" (arXiv:2606.04990, v4 2026-06-28)

- **Source/Date:** Yiqi Wang et al. (Griffith University + 8 institutions), cs.CR, v4 Jun 28, 2026. [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4]
- **Features:** taxonomy across trace sources (reasoning, retrieval, tools, **MCP boundaries**, memory, environment, multi-agent comms); provenance relations including **Support, Derive, Depend-on, Contradict, Invalidate, Trigger, Update**; trust functions (verification, attribution, debugging, safety enforcement, audit, failure attribution, recovery).
- **Overlap with AegisTrace:** **VERY HIGH on problem statement.** The survey's named gaps are AegisTrace's feature list: (a) "no benchmark family provides strong end-to-end coverage"; (b) missing typed provenance-relation annotations; (c) "systems detect unsafe behavior but rarely use provenance to **invalidate stale memory, quarantine contaminated evidence**, retry, roll back, or request approval"; (d) "existing standards (W3C PROV-DM, OpenTelemetry, PROV-AGENT) don't fully capture agent-specific semantic and procedural objects"; (e) execution-provenance metrics (trace completeness, provenance accuracy, **dependency coverage**, temporal consistency) have "no agreed definitions." [DOCUMENTED-BY-SOURCE]
- **Differences:** it's a survey/benchmark analysis, not a working system; it does not discuss expected-vs-observed comparison or certificates explicitly. [DOCUMENTED-BY-SOURCE for the covered content]
- **White space:** AegisTrace can position as the *working system* that closes the survey's recovery/invalidation gap and defines the missing metrics. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://arxiv.org/html/2606.04990v4

### 2.2 PROV-AGENT (arXiv:2508.02866; IEEE e-Science 2025)

- **Source/Date:** Souza, Gueroudji, DeWitt, Rosendo, Ghosal, Ross, Balaprakash, Ferreira da Silva (Oak Ridge-led); submitted Aug 4, 2025; accepted at IEEE e-Science 2025. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2508.02866]
- **Features:** provenance model extending **W3C PROV + MCP**; near-real-time open-source capture system; cross-facility (edge/cloud/HPC) evaluation for "critical provenance queries and agent reliability analysis."
- **Overlap:** **HIGH** — the closest *infrastructure* prior art: it also builds a provenance graph of agent executions including MCP.
- **Differences:** capture + querying only; abstract describes no expected-vs-observed deviation detection, no trust propagation/scores, no output invalidation, no quarantine. [DOCUMENTED-BY-SOURCE — abstract scope; full-text confirmation recommended]
- **White space:** everything AegisTrace adds *on top of* capture: comparison, trust, invalidation, certificates. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://arxiv.org/abs/2508.02866

### 2.3 NeuroTaint (arXiv:2604.23374, 2026)

- **Source/Date:** arXiv 2026 ("we present NeuroTaint, the first comprehensive taint tracking framework tailored for the unique information flow characteristics of LLM agents"). [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2604.23374v1]
- **Overlap:** HIGH for the *taint propagation* component of AegisTrace (trust/compromise propagation ≈ taint with a trust polarity).
- **Differences:** taint tracking ≠ trust attestation: no expected graphs, no certificates, no output invalidation workflow (per available content). [HYPOTHESIS]
- **Confidence:** MEDIUM-HIGH (preprint; not peer-verified). **Link:** https://arxiv.org/html/2604.23374v1

### 2.4 Who&When (arXiv:2505.00212; ICML 2025 Spotlight)

- **Source/Date:** Shaokun Zhang et al., May 2025; ICML 2025 Spotlight; ~213 citations. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2505.00212]
- **Features:** first benchmark for **automated failure attribution** in LLM multi-agent systems — "which agent" and "which step" caused the failure; dataset from 127 multi-agent systems (184 annotated failure tasks on HF); best method 53.5% accuracy.
- **Overlap:** MEDIUM-HIGH — attribution-over-logs is the *diagnostic* cousin of AegisTrace's causal analysis; also a natural benchmark/import source.
- **Differences:** post-hoc LLM-based reasoning over logged trajectories; no runtime enforcement, no trust propagation, no invalidation. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://arxiv.org/abs/2505.00212

### 2.5 AgentAuditor (arXiv:2506.00641; NeurIPS 2025)

- **Source/Date:** Luo et al., 2025; NeurIPS 2025; ~90 citations. [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2506.00641]
- **Features:** "universal, training-free, memory-augmented reasoning framework" for human-level safety/security evaluation of LLM agents (with ASSEBench).
- **Overlap:** MEDIUM — evaluation/audit over agent behavior; LLM-as-judge rather than causal-graph verification.
- **Differences:** no provenance graph, no cryptographic attestation. [HYPOTHESIS]
- **Confidence:** HIGH. **Link:** https://arxiv.org/abs/2506.00641

### 2.6 Runtime enforcement / IFC systems named by the survey (verified only via the survey)

- **CaMeL, FIDES, AgentSpec, Progent, AgentBound, Agent-Sentry, TRAIL, AgenTracer, LADYBUG, MAST, AgentTrace, PaperTrail, AgentOps** — systems/benchmarks in the runtime-guardrail, information-flow-control, and debugging space cited by the survey. [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4 names them; individual papers **UNVERIFIED this session** except where independently confirmed above.]
- **Watchdog:** no dedicated agent-provenance paper named "Watchdog" found in searches; the name appears only in unrelated contexts. Treat the brief's "Watchdog" as **UNVERIFIED / likely conflated**. [OBSERVED — searches returned no match]

### 2.7 RAG provenance / attribution

- The survey covers evidence-attribution metrics (**ALCE, FActScore, RAGTruth, RAGChecker, RAGAS, FEVER, SourceCheckup**) as "Established" for *attribution* (which evidence supports which claim) [DOCUMENTED-BY-SOURCE — survey]. This is *semantic* provenance for RAG content.
- **Gap vs AegisTrace:** attribution answers "which document supports this sentence"; AegisTrace answers "was the *pipeline that produced this output* the pipeline we trusted, and is the output still valid after a dependency was compromised." Complementary, not overlapping. [HYPOTHESIS]

---

## 3. ML model/data lineage signing

- **sigstore/model-transparency** (formerly model-signing): signs ML models via Sigstore; signatures/certificates stored in a transparency log. https://github.com/sigstore/model-transparency [O]; https://blog.sigstore.dev/model-transparency-v1.0/ [D]. OpenSSF **Model Signing (OMS)** spec introduced June 25, 2025; `model-signing` on PyPI. https://openssf.org/blog/2025/06/25/an-introduction-to-the-openssf-model-signing-oms-specification/ [D].
  - **Overlap:** LOW-MEDIUM — same trust substrate (Sigstore), different object (static model artifacts vs. executions).
  - **White space:** execution-level certificates complement artifact-level signatures; AegisTrace certificates should *reference* model signatures. [HYPOTHESIS]
- **CycloneDX ML-BOM / SPDX AI+Dataset profiles:** inventory standards for models/datasets (see standards.md). Overlap LOW; reuse as import/export. [D]
- **Witness / in-toto attestations for ML pipelines:** attest *training/build steps*; AegisTrace attests *inference/execution*. [HYPOTHESIS]

---

## 4. Commercial products claiming runtime AI-agent integrity / attestation

Fair summary based on public materials reviewed this session:

| Vendor/product | Claimed runtime-integrity capability | What is verifiable publicly |
|---|---|---|
| **AgentSign** (community; agentsign.dev) | Identity certs + signed execution chains (DAG of I/O hashes) + hash-based runtime code attestation + output tamper detection + cryptographic trust scoring; "patent pending" | HN thread documents all five subsystems and criticisms (signatures prove what was sent, not that the signer wasn't compromised; hash checks bypassable via env injection/lazy loading) [O — https://news.ycombinator.com/item?id=47325206] |
| **Cisco AI Defense** | "End-to-end AI security… protect AI development, deployment, and usage" | Product page + acquisition page; no public causal-provenance/expected-vs-observed technical detail found [D — https://www.cisco.com/site/us/en/products/security/ai-defense/robust-intelligence-is-part-of-cisco/index.html] |
| **Palo Alto Prisma AIRS** (w/ Protect AI) | "comprehensive protection for the entire AI lifecycle" incl. scanning, LLM security, red teaming | Press release; no public runtime causal attestation detail [D — https://www.paloaltonetworks.com/company/press/2025/palo-alto-networks-completes-acquisition-of-protect-ai] |
| **Zenity** | "adaptive security and governance from buildtime to runtime" for AI agents | Marketing site; technical mechanism unpublished [D — https://zenity.io/] |
| **Prompt Security (SentinelOne)** | "runtime security for GenAI and agentic AI" (reported positioning) | Acquisition coverage; technical detail unpublished [D] |
| **Lasso Security** | "visibility, control, and protection across AI models, agents, and apps" incl. MCP gateway | Marketing site [D — https://www.lasso.security/] |
| **Snyk (Invariant Labs)** | Agent component scanning (snyk/agent-scan: agents, MCP servers, skills) + AI Trust Platform | GitHub repo + acquisition coverage [O/D — https://github.com/snyk/agent-scan] |
| **OVERT (community standard)** | Runtime trust requirements for AI systems incl. MCP server runtime attestation | Standard PDF v1.1 [O — https://overt.is/OVERT_v1.1_STANDARD.pdf] |
| **TRACE (OPAQUE/AMD/Intel/TII)** | "Trust, Runtime Attestation and Compliance Evidence" standard for AI | Surfaced in searches; primary page UNVERIFIED |

- **Key observation:** no vendor reviewed publishes an architecture that (a) constructs a causal provenance graph of AI executions, (b) compares it against a declared expected graph, (c) propagates trust/compromise through dependencies, and (d) invalidates/re-certifies outputs with signed certificates. Public materials reviewed may lag private capability — re-check quarterly. [HYPOTHESIS grounded in D sources above]

---

## 5. Patents (Google Patents / Justia — as found this session)

| # | Patent / application | Assignee | Dates | What it claims (2-line summary) | Overlap assessment | Confidence |
|---|---|---|---|---|---|---|
| P1 | **US11423146B2** (pub. as **US20210064751A1**), "Provenance-based threat detection tools and stealthy malware detection"; app. US16/991,288 | NEC (orig. NEC Laboratories America) | Pub. 2021-03-04; granted 2022-08-23; active, adj. expiry 2040-11-14 | Builds a provenance graph from system data, samples it into linear paths, ranks by regularity score, embeds the K rarest paths as vectors, flags anomalies (one-class SVM/LOF), **terminates the associated process** | **Direct conceptual overlap** with provenance-graph anomaly detection + automated response; on OS events, path-embedding based; no AI semantics, no expected-vs-observed, no output invalidation/certificates | HIGH (fetched full page) — https://patents.google.com/patent/US20210064751A1/en |
| P2 | **US12081569B2**, "Graph-based analysis of security incidents" | (per Google Patents listing; assignee page not fetched) | Published/granted 2024 (exact dates UNVERIFIED) | Graph-based computational methods to analyze security incidents in networks post-mortem | MEDIUM overlap: graph analytics for security incidents; scope appears forensic/network rather than runtime AI attestation | MEDIUM — https://patents.google.com/patent/US12081569B2/en |
| P3 | **US20180219888A1**, "Graph-Based Network Security Threat Detection Across Time and Systems" | (assignee page not fetched) | Pub. 2018 | Graph-based network security analytic framework combining multiple information sources over time | LOW-MEDIUM overlap: multi-source graph analytics for network threats | MEDIUM — https://patents.google.com/patent/US20180219888A1/en |
| P4 | **US20250086270A1**, "Large Language Model (LLM) Supply Chain Security" | (assignee page not fetched) | Pub. 2025 | "LLM attestations" (harmful-content attestation, bias-mitigation attestation) with scores/verification status in a supply-chain pipeline | **MEDIUM-HIGH overlap** on the phrase "LLM attestation"; appears content-safety-oriented rather than execution-provenance oriented — read claims before drawing conclusions | MEDIUM (title/abstract via search) — https://patents.google.com/patent/US20250086270A1/en |
| P5 | **WO2021236551A1**, "Methods and apparatus for attestation of an artificial intelligence model" | (assignee page not fetched) | Pub. 2021 | AI-model attestation incl. attestation result generator capable of offline attestation | MEDIUM overlap: attestation of AI *models* (static), not executions | MEDIUM — https://patents.google.com/patent/WO2021236551A1/en |
| P6 | **US20250259042A1 / US20250259044A1**, "Platform for Orchestrating a Scalable, Privacy-Preserving LLM Platform" | (assignee page not fetched) | Pub. 2025 | LLM orchestration on TEEs with secure boot, **runtime attestation**, isolated memory, cryptographic proofs of security posture | **MEDIUM-HIGH overlap** on "runtime attestation of LLM serving"; hardware/posture attestation rather than behavioral provenance | MEDIUM — https://patents.google.com/patent/US20250259042A1/en |
| P7 | **US12316655B1**, "Cyber Resilience Agentic Mesh" | (assignee page not fetched) | Granted 2025 (exact date UNVERIFIED) | LLM-based agent mesh collecting multiple attestations over time | MEDIUM overlap: agent mesh + collected attestations | LOW-MEDIUM (title/abstract only) — https://patents.google.com/patent/US12316655B1/en |
| P8 | **US20240305465A1**, "Artificial intelligence model accuracy validation" | (assignee page not fetched) | Pub. 2024 | LLM/model accuracy validation with attestation-verification components | LOW-MEDIUM: validation-attestation combo | LOW-MEDIUM — https://patents.google.com/patent/US20240305465A1/en |
| P9 | **US20260252995**, "Systems, Methods, and …" (abstract references a **revocation controller propagating invalidation events across workloads, sessions, and derived artifacts**) | **UNVERIFIED** (Justia returned 403; fetch later) | Pub. 2026 | Propagating invalidation events across workloads/sessions/derived artifacts | **Potentially the closest to AegisTrace's output-invalidation claim** — must be analyzed by counsel; note domain appears to be workloads/compute, possibly not AI | MEDIUM (abstract only) — https://patents.justia.com/patent/20260252995 |
| P10 | **US8990948B2**, "Systems and methods for orchestrating runtime operational integrity" | (assignee page not fetched) | Granted ~2015 | Runtime attestation measured by a trust agent within execution | LOW overlap: classic host runtime attestation, pre-AI | MEDIUM — https://patents.google.com/patent/US8990948B2/en |
| P11 | **CN120915513A**, AI agent data protection method based on controlled (remote attestation of inference code) | (CN filing) | Pub. 2025/2026 | AI agents verified via remote attestation that inference code is untampered + access control | MEDIUM: attestation for agent inference code | LOW-MEDIUM — https://patents.google.com/patent/CN120915513A/en |
| P12 | **US8682795B2**, "Trusted information exchange based on trust agreements" | (assignee page not fetched) | Granted ~2014 | Trust propagation across agencies/enterprises via trust agreements | LOW: generic trust propagation concept | MEDIUM — https://patents.google.com/patent/US8682795B2/en |

**Patent-search caveats:** queries were run through web search over patents.google.com/Justia; Google Patents' full engine (semantic/claim search, legal-status fields, family data) was not directly queryable this session (page fetches mostly 403/404). Assignees marked "(page not fetched)" must be confirmed by counsel. [OBSERVED limitation]

---

## 6. White-space synthesis (technical, not legal)

**What the prior art does NOT do (verified across sources above):**
1. **No system reviewed builds an execution-time causal provenance graph over AI/agent semantics** (model, prompt, retrieval, tools, MCP, dependencies) *and* treats it as the unit of verification. Closest: PROV-AGENT (capture/query only) [D]; AgentSign (hash-chain, not causal semantics) [O].
2. **No reviewed work compares an OBSERVED execution graph against a declared EXPECTED graph** and uses the deviation as the security signal. HOLMES compares against TTP *attack* patterns, not declared *benign* expectations. [HYPOTHESIS from verified sources]
3. **Trust propagation over AI causal graphs with output consequences** (quarantine/invalidate/re-certify outputs) is explicitly named as an open gap by the June 2026 survey ("rarely use provenance to invalidate stale memory, quarantine contaminated evidence…") [D — https://arxiv.org/html/2606.04990v4]. NoDoze/RapSheet prove the algorithmic machinery works on hosts, but no reviewed work applies it to AI outputs with signed consequences.
4. **Verifiable per-execution "AI Trust Certificates"** (signed, in-toto-style, carrying expected/observed digests + deviation verdict) appear in no reviewed product, paper, or standard; the community standards OVERT/TRACE and the AgentSign project signal demand but not a mature artifact. [HYPOTHESIS from O/D sources]
5. **Patent landscape:** adjacent clusters exist (provenance-graph anomaly detection + response: P1; TEE runtime attestation for LLM serving: P6; invalidation propagation: P9; LLM supply-chain attestations: P4), but no reviewed claim covers the *combination* on AI execution graphs. This is precisely where counsel should focus a proper search. [HYPOTHESIS]

**Biggest threats to the white space (what to watch):**
- The 2026 survey shows the academic community has *identified* every AegisTrace ingredient — expect system papers within 6–12 months. [HYPOTHESIS]
- AgentSign claims "patent pending" on a trust-scoring/execution-chain design; its HN criticism (hash-only attestation bypassed by context manipulation) actually maps AegisTrace's differentiation, but its filing could constrain claims. [O — HN thread]
- Platform vendors (Cisco/PANW/SentinelOne/Check Point) have the telemetry and the customers; if any adds provenance-based verification, the window narrows. [HYPOTHESIS]

*Again: the above are technical novelty hypotheses for engineering prioritization and benchmark design — not legal conclusions. Engage patent counsel.*
