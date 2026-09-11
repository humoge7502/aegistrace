# AegisTrace — Standards Analysis & Recommended Standards Posture

**Status:** Research deliverable (prior-art + standards workstream)
**Date of research:** 2026-09-12
**Claim tagging convention:** every factual claim is tagged `[DOCUMENTED-BY-SOURCE]` (verified against the linked source during this research), `[OBSERVED]` (directly observed by this agent, e.g., a fetched page/repo), or `[HYPOTHESIS]`. Items that could not be verified are marked **UNVERIFIED**.

> Scope note: this document maps standards and emerging norms relevant to AegisTrace ("Continuous AI Execution Attestation / Runtime Causal Trust") and states, per standard, what AegisTrace should **REUSE**, what it should **BUILD ON TOP OF**, and what **GAPS** remain that justify AegisTrace's existence.

---

## 1. SLSA (Supply-chain Levels for Software Artifacts) — v1.x

**What it is / standardizes** [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.2/ and https://slsa.dev/spec/v1.1/]:
- A specification for describing and incrementally improving supply-chain security, organized into levels of increasing guarantees, governed by The Linux Foundation under the Community Specification License 1.0.
- **SLSA v1.2 is the current version** (status "Approved", © 2026 The Linux Foundation); v1.1 is listed as *Retired* on the slsa.dev site [OBSERVED — https://slsa.dev/spec/v1.1/ states "Retired — Version 1.2 is the current version of the spec"].
- v1.2 vs v1.1 changes: adds a **Source Track**, updates the threat model, and restructures the spec to support multiple tracks [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.2/whats-new]. No release date is published on the whats-new page [OBSERVED].
- Build track levels: **Build L0 (no guarantees) → L1 (provenance exists) → L2 (hosted build platform) → L3 (hardened builds)** [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.1/levels].
- The **Provenance and VSA formats are recommended but not required by the specification** [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.2/].
- SLSA v1.0 was announced by OpenSSF on 2023-04-19 [DOCUMENTED-BY-SOURCE — https://openssf.org/press-release/2023/04/19/openssf-announces-slsa-version-1-0-release/].

**Provenance format (SLSA Provenance v1):** an in-toto attestation whose predicate contains `buildDefinition` (external/internal parameters, `resolvedDependencies`) and `runDetails` (builder, byproducts, metadata) [DOCUMENTED-BY-SOURCE — https://slsa.dev/spec/v1.1/provenance, linked as "Suggested provenance format" from the v1.2 index]. Field-level detail is from the spec's suggested format; treat exact JSON shapes as subject to the live spec page.

**AegisTrace REUSE:**
- Use **SLSA Build L1–L3 provenance for the components that produce AegisTrace itself** (backend image, SDK wheel, frontend bundle) and require SLSA provenance for third-party dependencies we ingest as *expected-graph nodes* [HYPOTHESIS → design decision].
- Model the **"expected execution graph" declaratively the way SLSA models expected builds**: externalParameters ≈ prompt/policy/config; resolvedDependencies ≈ model + tools + MCP servers + retrieval sources. This gives a familiar, spec-shaped analogy in docs and pitches [HYPOTHESIS].

**BUILD ON TOP OF:** SLSA covers **artifact construction**, not **execution**. There is no SLSA track for "runtime execution of an AI agent," no expected-vs-observed comparison, and no trust propagation at runtime [DOCUMENTED-BY-SOURCE — v1.2 index describes only Source/Build tracks; gap is an inference = HYPOTHESIS].

**GAPS:** No execution-time levels, no notion of a model/tool/MCP-server as a provenance *subject at inference time*, no output invalidation semantics. (Also nothing about AI/model provenance on the v1.2 index page [OBSERVED].)

---

## 2. in-toto + the in-toto Attestation Framework (incl. ITE-6/7/8)

**What it standardizes** [DOCUMENTED-BY-SOURCE — https://in-toto.io/ and https://github.com/in-toto/attestation]:
- in-toto is a CNCF **graduated** project: "a framework to secure the integrity of software supply chains… an open, extensible metadata standard," Apache-licensed libraries [DOCUMENTED-BY-SOURCE — https://in-toto.io/].
- The **Attestation Framework repo (`in-toto/attestation`)** hosts "a specification for generating verifiable claims about any aspect of how a piece of software is produced," with the core spec at `spec/v1`, vetted predicates at `spec/predicates`, and protobuf + Go/Python/Rust/Java bindings [OBSERVED — https://github.com/in-toto/attestation].
- The **Statement envelope** (subject / predicateType / predicate, wrapped in DSSE signatures) is the core format; predicate design guidance lives at `docs/new_predicate_guidelines.md` [OBSERVED — repo README; exact field list from spec/v1 not re-quoted here, see https://github.com/in-toto/attestation/tree/main/spec].

**ITE status (in-toto Enhancement Proposals)** [OBSERVED — https://github.com/in-toto/ITE]:
- **ITE-6 "Enabling contextual in-toto attestations" — Accepted.** This is the layered-attestation / referencing-attestations work.
- **ITE-7 "Signing & Verification With X509" — Draft.**
- **ITE-9 "Introducing new in-toto Attestation types" — Accepted.**
- **ITE-8 is not listed** in the ITE repo README (neither accepted nor draft) [OBSERVED]; community references to an "ITE-8" could not be confirmed — treat any ITE-8 claim as **UNVERIFIED**.
- Note: the user hypothesis that ITE-7 = "traceability" is **corrected** — per the ITE repo, ITE-7 is X.509 signing/verification [OBSERVED].

**AegisTrace REUSE (this is the single most important reuse decision):**
- Emit **AI Trust Certificates as DSSE-wrapped in-toto Statements with a custom predicate type**, e.g. `https://aegistrace.dev/attestations/execution-trust/v1`, with predicate fields for: execution id, expected-graph digest, observed-graph digest, deviation report digest, trust scores, quarantine/re-certification decisions [HYPOTHESIS → recommended concrete posture; see §16].
- Use ITE-6-style **layered/contextual attestations** to link: build attestations (SLSA) → model attestations (model signing) → execution attestations (AegisTrace) so each certificate references the layers below it [HYPOTHESIS; mechanism consistent with ITE-6 title "contextual in-toto attestations" [OBSERVED]].
- Reuse `in-toto` Python lib for signing/verification in the SDK (Python/FastAPI stack) [HYPOTHESIS].

**GAPS:** in-toto predicates are about **software production steps**; there is no predicate for *inference-time execution graphs*, no concept of **expected-vs-observed deviation**, and no **trust propagation or output invalidation** semantics. This is AegisTrace's standards gap and opportunity [HYPOTHESIS, grounded in the observed scope of the spec].

---

## 3. Sigstore / Cosign (incl. keyless status)

**What it standardizes / provides** [DOCUMENTED-BY-SOURCE — https://docs.sigstore.dev/ and https://docs.sigstore.dev/cosign/signing/overview/]:
- Sigstore is **GA** ("production grade stable services for artifact signing and verification"); **Cosign 2.0** was the release that followed GA [DOCUMENTED-BY-SOURCE — https://blog.sigstore.dev/cosign-2-0-released/].
- **Keyless signing is the documented core mode**: OIDC-identity-based signing with **ephemeral keys and short-lived certificates from Fulcio**, transparency logging in **Rekor** [DOCUMENTED-BY-SOURCE — https://docs.sigstore.dev/cosign/signing/overview/]. Common CI integrations: GitHub Actions OIDC, GitLab CI/CD [DOCUMENTED-BY-SOURCE — same page].

**AegisTrace REUSE:**
- Sign AI Trust Certificates (the in-toto statements above) with **Sigstore keyless** from the AegisTrace backend's CI, and optionally from customer deployments with their own OIDC identities [HYPOTHESIS].
- Publish certificate digests to Rekor so third parties can detect issuance events [HYPOTHESIS].

**GAPS:** Sigstore proves *who signed what, when* — it has no semantics for *what the signature means* (that is the predicate's job), no runtime observation model, no deviation detection, no trust propagation [HYPOTHESIS — consistent with observed scope of docs].

---

## 4. SPDX 3.0

**What it standardizes** [DOCUMENTED-BY-SOURCE — https://fossa.com/blog/spdx-3-0/ and https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf]:
- **SPDX 3.0.0 released April 2024** (FOSSA dates it April 17, 2024), Linux Foundation; major rewrite into an object model with **profiles**, including an **AI Profile** ("outputs of the AI development process") and a **Dataset Profile** (dataset type, size, collection, preparation, intended use), plus Security and Build profiles. **SPDX 3.0.1** followed (PDF December 2024).

**AegisTrace REUSE:** Use SPDX 3.0 AI/Dataset profiles to describe **static** components of the expected graph (models, datasets, their provenance) when exchanging with governance tooling; map SPDX elements ↔ AegisTrace graph nodes in the SDK [HYPOTHESIS].

**GAPS:** SPDX is **inventory/lineage metadata**, not runtime execution evidence; no deviation, trust, or invalidation semantics [HYPOTHESIS].

---

## 5. CycloneDX 1.6 (incl. AI/ML-BOM profile)

**What it standardizes** [DOCUMENTED-BY-SOURCE — https://cyclonedx.org/capabilities/mlbom/ and https://cyclonedx.org/capabilities/mlbom/ ecosystem pages]:
- CycloneDX is OWASP-stewarded and standardized as **ECMA-424** [DOCUMENTED-BY-SOURCE — https://github.com/cyclonedx/specification].
- **ML-BOM capability** documents "datasets, models, and configurations for AI/ML systems," dataset provenance, training methodologies, framework configuration, and risks around bias/data integrity/model security [DOCUMENTED-BY-SOURCE — https://cyclonedx.org/capabilities/mlbom/].
- Community/secondary sources (flagged as secondary): ML-BOM support began in **v1.5 (2023)** and was extended in **v1.6 (2024)**, which also added **CBOM (cryptographic BOM)**; `modelCard` embeds structured AI documentation (considerations, model parameters, datasets, quantitative analysis), `modelCard.data` captures training/evaluation datasets, and algorithmic components describe learning types/model-architecture families [DOCUMENTED-BY-SOURCE — https://www.reversinglabs.com/blog/cyclonedx-16-upgraded-for-the-evolving-software-supply-chain-security-era and https://cyclonedx.org/capabilities/mlbom/]. The official capability page itself does not enumerate schema fields [OBSERVED]; verify exact field names against the 1.6 schema JSON before implementation.

**AegisTrace REUSE:** CycloneDX ML-BOM as an **export format** for the static layer of the expected graph; accept CycloneDX 1.6 AIBOM/ML-BOM as an input when customers already generate them [HYPOTHESIS].

**GAPS:** An ML-BOM says what components *exist*, not what *happened at runtime*; no causal links between retrievals/tools/prompts/outputs, no expected-vs-observed comparison, no trust propagation [HYPOTHESIS].

---

## 6. OpenTelemetry GenAI Semantic Conventions

**Status (important)** [DOCUMENTED-BY-SOURCE — https://opentelemetry.io/docs/specs/semconv/gen-ai/ and https://github.com/open-telemetry/semantic-conventions-genai]:
- The GenAI semantic conventions **have moved out of the main semconv repo into a dedicated repository: `open-telemetry/semantic-conventions-genai`**; the old opentelemetry.io pages redirect and are no longer maintained [DOCUMENTED-BY-SOURCE — https://opentelemetry.io/docs/specs/semconv/gen-ai/].
- There is a working doc for **"Semantic Conventions for GenAI agent and framework spans"** (`gen-ai-agent-spans.md`) covering agent execution/invocation telemetry [DOCUMENTED-BY-SOURCE — https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md].
- Stability: **most GenAI conventions (incl. agent spans) remain Development/Experimental** and can change without notice; `gen_ai.agent.name`, `gen_ai.agent.id`, `gen_ai.operation.name` etc. exist in the attribute registry [DOCUMENTED-BY-SOURCE — search-confirmed across multiple secondary sources incl. docs referencing the repo; treat specific attribute names as subject to change].

**AegisTrace REUSE:** Adopt OTEL GenAI spans/attributes as the **observation layer**: the AegisTrace SDK emits OTEL-compatible spans for model calls, tool calls, MCP calls, retrievals; AegisTrace graph edges are derived from these spans. This keeps AegisTrace non-competitive with observability vendors and lowers integration cost [HYPOTHESIS].

**GAPS:** OTEL semconv are **telemetry naming/structure**, not security semantics: no expected/expected-vs-observed model, no integrity, no trust, no invalidation. Also instability risk while in Development status [HYPOTHESIS + DOCUMENTED-BY-SOURCE for status].

---

## 7. OCI (image spec, artifacts, referrers)

**What it standardizes** [OBSERVED — https://github.com/opencontainers/image-spec; referrers support in image-spec v1.1 is known from the OCI release notes — UNVERIFIED this session]: container image/artifact format and distribution; the **Referrers API** allows attaching artifacts (e.g., attestations/SBOMs) to other artifacts.

**AegisTrace REUSE:** Store AI Trust Certificates as **OCI referrer artifacts** attached to signed model/tool images (cosign/ORS-style), so certificates live next to the artifacts they attest in existing registries [HYPOTHESIS; mechanism mirrors how cosign attaches attestations — UNVERIFIED this session]. Fallback: store certificates in PostgreSQL with an OCI-compatible digest scheme.

---

## 8. W3C PROV / PROV-JSON

**What it standardizes** [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4 (survey) confirms W3C PROV-DM as the base provenance standard; PROV-JSON is a W3C Note — UNVERIFIED this session for the exact note URL]: PROV-DM defines entities/activities/agents and derivation/usage/generation relations — the canonical causal provenance model.

**AegisTrace REUSE:** Map the AegisTrace execution graph to PROV (entity=model/dataset/tool/document, activity=model call/tool call/agent step, agent=MCP server/agent). Academic work in this exact space already extends PROV for agents — **PROV-AGENT (arXiv:2508.02866)** extends W3C PROV + MCP for agentic workflows [DOCUMENTED-BY-SOURCE — https://arxiv.org/abs/2508.02866]. Provide PROV-JSON export for interoperability/academic benchmarking [HYPOTHESIS].

**GAPS:** PROV has no **expected-vs-observed comparison**, no trust scoring, no invalidation semantics beyond generic relations (the 2026 survey explicitly lists "unified trace schemas" as a gap: "existing standards (W3C PROV-DM, OpenTelemetry, PROV-AGENT) don't fully capture agent-specific semantic and procedural objects" [DOCUMENTED-BY-SOURCE — https://arxiv.org/html/2606.04990v4]).

---

## 9. NIST: AI RMF, SP 800-207, and the "SP 800-227" correction

- **NIST AI RMF 1.0** — voluntary risk-management framework (GOVERN/MAP/MEASURE/MANAGE) [DOCUMENTED-BY-SOURCE — https://www.nist.gov/itl/ai-risk-management-framework]; **NIST AI 600-1** is the Generative AI Profile [DOCUMENTED-BY-SOURCE — https://www.nist.gov/itl/ai-risk-management-framework; referenced in search results].
- **NIST SP 800-207 Zero Trust Architecture** (Aug 2020) — the canonical zero-trust reference: never trust, always verify, assume breach, per-request authorization [DOCUMENTED-BY-SOURCE — general knowledge; the publication page https://csrc.nist.gov/pubs/sp/800/207/final was not fetched this session — UNVERIFIED this session but uncontroversial]. AegisTrace's "trust is computed per execution from observed evidence" maps to zero-trust rhetoric for the AI stack [HYPOTHESIS].
- **CORRECTION to a prior project hypothesis:** **NIST SP 800-227 is NOT about AI attestation.** SP 800-227 is **"Recommendations for Key-Encapsulation Mechanisms (KEMs)"** (post-quantum crypto); its initial public draft was released for comment on **January 7, 2025**, and the final publication was announced in 2025 [DOCUMENTED-BY-SOURCE — https://csrc.nist.gov/news/2025/draft-sp-800-227-is-available-for-comment and https://csrc.nist.gov/news/2025/nist-publishes-sp-800-227]. **No NIST publication titled around "AIA attestations" was found** [OBSERVED across searches].
- The actually relevant NIST AI-security workstreams (2025–2026):
  - **COSAiS — SP 800-53 Control Overlays for Securing AI Systems**: concept paper released Aug/Sep 2025, overlays being developed [DOCUMENTED-BY-SOURCE — https://csrc.nist.gov/News/2025/control-overlays-for-securing-ai-systems, https://csrc.nist.gov/projects/cosais].
  - **NIST IR 8596 (preliminary draft) — Cybersecurity Framework Profile for AI ("Cyber AI Profile")**, IPD December 2025, comments through Jan 30, 2026 [DOCUMENTED-BY-SOURCE — https://csrc.nist.gov/pubs/ir/8596/iprd (per search results)].
  - **NIST AI 800-1 — AI agents risk-management guidance** (drafted for comment) [DOCUMENTED-BY-SOURCE — search results citing regulations.gov docket NIST-2025-0035; exact title UNVERIFIED].
  - **NIST SP 800-239 (IPD) — AI Data Center Security Analysis**, comment period through Sept 25, 2026 [DOCUMENTED-BY-SOURCE — https://csrc.nist.gov/News/2026/ai-data-center-security-analysis-draft-sp-800-239].

**AegisTrace REUSE:** Use AI RMF MEASURE/MANAGE language for the trust-scoring story; align the AegisTrace control set with COSAiS overlays and IR 8596 profile mappings as they finalize; cite SP 800-207 for the zero-trust framing [HYPOTHESIS].

**GAPS:** NIST has **no normative standard for runtime execution attestation of AI agents** — the closest is TEE-based attestation guidance elsewhere and the COSAiS control work; the gap is real and current [HYPOTHESIS grounded in the sources above].

---

## 10. EU AI Act (Regulation (EU) 2024/1689) — transparency & logging

**Key obligations** [DOCUMENTED-BY-SOURCE — https://artificialintelligenceact.eu/article/12/, https://artificialintelligenceact.eu/article/19/, https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai, https://www.lw.com/insights/2026/08/Deciphering-the-EU-AI-Act]:
- **Article 12 (Record-keeping):** "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system," sufficient to trace functionality, identify risk situations, support post-market monitoring (Art. 72), and deployer evaluations under Art. 26 [DOCUMENTED-BY-SOURCE — https://artificialintelligenceact.eu/article/12/].
- **Article 19:** providers keep Art. 12(1) logs **at least six months** unless other law requires longer [DOCUMENTED-BY-SOURCE — https://artificialintelligenceact.eu/article/19/].
- **GPAI obligations (Art. 53–55)** — technical documentation, copyright policy, training-data summaries; systemic-risk duties for GPAI with systemic risk — **applicable since 2 August 2025**; full penalty enforcement phases through 2026–2027 [DOCUMENTED-BY-SOURCE — https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai, https://www.lw.com/insights/2026/08/Deciphering-the-EU-AI-Act].

**AegisTrace REUSE/POSITION:** AegisTrace's per-execution provenance graphs + tamper-evident AI Trust Certificates are a strong technical answer to Art. 12 "automatic recording of events" and to Art. 72 post-market monitoring — a compliance narrative, not a compliance guarantee (AegisTrace is a tool, not a conformity assessment) [HYPOTHESIS]. The 6-month retention floor is a concrete product requirement (logs ≥ 6 months) [DOCUMENTED-BY-SOURCE → product requirement].

---

## 11. ISO/IEC 42001

**What it standardizes** [DOCUMENTED-BY-SOURCE — secondary sources in searches (ISMS.online etc.); the standard itself is paywalled — verify at https://www.iso.org/standard/81230.html before publishing claims]: an **AI Management System (AIMS)** standard (management-system approach à la ISO 27001) for organizational AI governance. Exact clause list **UNVERIFIED this session**.

**AegisTrace REUSE:** Position AI Trust Certificates as *evidence artifacts* that feed an ISO/IEC 42001 AIMS (records of monitoring, incident response, continual improvement) [HYPOTHESIS]. Do not claim "ISO 42001 certified" anything.

---

## 12. OWASP Top 10 for LLM Applications — 2025 version

**Current version verified** [DOCUMENTED-BY-SOURCE — https://genai.owasp.org/llm-top-10/ and https://owasp.org/www-project-top-10-for-large-language-model-applications/]:
- The current list is **"2025 Top 10 Risk & Mitigations for LLMs and Gen AI Apps"** (v2025, published late 2024; PDF: OWASP-Top-10-for-LLMs-v2025.pdf):
  1. LLM01:2025 Prompt Injection
  2. LLM02:2025 Sensitive Information Disclosure
  3. LLM03:2025 Supply Chain
  4. LLM04:2025 Data and Model Poisoning
  5. LLM05:2025 Improper Output Handling
  6. LLM06:2025 Excessive Agency
  7. LLM07:2025 System Prompt Leakage
  8. LLM08:2025 Vector and Embedding Weaknesses
  9. LLM09:2025 Misinformation (formerly Overreliance)
  10. LLM10:2025 Unbounded Consumption (formerly Model DoS)
  [DOCUMENTED-BY-SOURCE — https://owasp.org/www-project-top-10-for-large-language-model-applications/ and https://genai.owasp.org/llm-top-10/]

**AegisTrace mapping:** AegisTrace's expected-vs-observed deviation detection directly targets **LLM03 (Supply Chain)**, **LLM04 (Data/Model Poisoning)**, **LLM06 (Excessive Agency)**, and **LLM08 (Vector/Embedding Weaknesses)**; trust propagation + invalidation is the *detection and response* complement to OWASP's mostly *preventive* mitigations [HYPOTHESIS].

---

## 13. OWASP Agentic AI / Agentic Security Initiative (ASI)

**Status** [DOCUMENTED-BY-SOURCE — https://genai.owasp.org/initiatives/agentic-security-initiative/ and https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/]:
- OWASP Gen AI Security Project runs an **Agentic Security Initiative** with an **"Agentic AI — Threats and Mitigations"** guide (April 2025 PDF) and a **Top 10 risks for autonomous/agentic AI** workstream (threats incl. agent goal hijacking, tool misuse) [DOCUMENTED-BY-SOURCE — same links].
- Presented ASI taxonomy at RSAC 2025; active community events through 2025–2026 [DOCUMENTED-BY-SOURCE — https://genai.owasp.org/event/agentic-security-open-workshop-livestream-event-from-rsac-2025/].

**AegisTrace REUSE:** Adopt the ASI threat taxonomy in AttackBench scenarios and map AegisTrace detections to ASI threats (like a MITRE-ATT&CK-style coverage matrix) [HYPOTHESIS].

---

## 14. MITRE ATLAS

**What it is** [DOCUMENTED-BY-SOURCE — https://atlas.mitre.org/ (canonical site); content not re-fetched this session — the site is the authoritative reference]: MITRE ATLAS (Adversarial Threat Landscape for AI Systems) is the ATT&CK-style knowledge base of adversarial tactics/techniques against ML systems and AI-enabled defenses.

**AegisTrace REUSE:** Encode AttackBench attacks with ATLAS technique IDs so detections are expressed in a recognized vocabulary; classic provenance-graph literature already maps to ATT&CK TTPs (see prior-art.md on HOLMES) [HYPOTHESIS; HOLMES TTP-mapping is DOCUMENTED-BY-SOURCE via https://arxiv.org/abs/1810.01594].

---

## 15. Other standards worth tracking (brief)

- **VEX/CISA** (vulnerability exploitability exchange): not core to AegisTrace; consider VEX-style "not affected" statements when a compromised component is later cleared — a re-certification receipt [HYPOTHESIS].
- **DSSE** (Dead Simple Signing Envelope): the signature wrapper for in-toto statements; reuse as-is [DOCUMENTED-BY-SOURCE — referenced by in-toto attestation framework; see https://github.com/secure-systems-lab/dsse — UNVERIFIED this session].
- **MCP (Model Context Protocol):** the tool/integration layer whose servers are first-class AegisTrace graph nodes; MCP server attestations are already appearing in community standards (e.g., OVERT requires "CUSTOM MCP SERVER RUNTIME ATTESTATION" [DOCUMENTED-BY-SOURCE — https://overt.is/OVERT_v1.1_STANDARD.pdf]).

---

## 16. Recommended "standards posture" for the implementation (concrete)

1. **Certificate format:** Every AI Trust Certificate is a **DSSE envelope containing an in-toto Statement** with `predicateType: https://aegistrace.dev/attestations/execution-trust/v1` and a JSON predicate: `{execution_id, timestamp, expected_graph_digest, observed_graph_digest, deviations[], trust_state, quarantined_outputs[], recertification_of}`. [HYPOTHESIS → spec decision]
2. **Signing:** Sigstore **keyless** (Fulcio/Rekor) in CI; optional KMS-based signing for on-prem customers. Cosign-compatible verification path for the certificates attached to images. [HYPOTHESIS]
3. **Observation layer:** OpenTelemetry GenAI semantic conventions (agent/tool spans from `semantic-conventions-genai`) for span naming; AegisTrace adds its own security attributes under a dedicated namespace (e.g., `aegis.*`) since GenAI semconv are still Development status. [HYPOTHESIS]
4. **Static component inventory:** import/export **CycloneDX 1.6 ML-BOM** and **SPDX 3.0 AI/Dataset profiles**; the internal canonical model is AegisTrace's own graph (not either BOM format). [HYPOTHESIS]
5. **Graph model:** W3C PROV-aligned internal semantics (entity/activity/agent + derivedFrom/used/generated), with PROV-JSON export for interoperability. [HYPOTHESIS]
6. **Artifact storage:** certificates stored in PostgreSQL (queryable) AND publishable as **OCI referrer artifacts** for registry-native distribution. [HYPOTHESIS]
7. **Standards interaction strategy:** contribute the execution-trust predicate to the in-toto attestation predicates repo (`in-toto/attestation` accepts community predicates [OBSERVED]); track COSAiS/IR 8596 for control mappings; cite EU AI Act Art. 12/19 and OWASP ASI in compliance documentation. [HYPOTHESIS]
8. **Do NOT** re-implement: signing (Sigstore), envelope (DSSE), build provenance (SLSA), telemetry naming (OTEL), BOM schemas (CDX/SPDX). **Do** own: expected-vs-observed graph comparison, trust propagation, invalidation/quarantine, re-certification, certificate semantics. [HYPOTHESIS]

---

### Source index (standards.md)
- SLSA: https://slsa.dev/spec/v1.2/ · https://slsa.dev/spec/v1.2/whats-new · https://slsa.dev/spec/v1.1/ (retired) · https://slsa.dev/spec/v1.1/levels · https://openssf.org/press-release/2023/04/19/openssf-announces-slsa-version-1-0-release/
- in-toto: https://in-toto.io/ · https://github.com/in-toto/attestation · https://github.com/in-toto/ITE
- Sigstore: https://docs.sigstore.dev/cosign/signing/overview/ · https://blog.sigstore.dev/cosign-2-0-released/
- SPDX: https://fossa.com/blog/spdx-3-0/ · https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf
- CycloneDX: https://cyclonedx.org/capabilities/mlbom/ · https://github.com/cyclonedx/specification · https://www.reversinglabs.com/blog/cyclonedx-16-upgraded-for-the-evolving-software-supply-chain-security-era
- OTEL: https://opentelemetry.io/docs/specs/semconv/gen-ai/ · https://github.com/open-telemetry/semantic-conventions-genai
- NIST: https://www.nist.gov/itl/ai-risk-management-framework · https://csrc.nist.gov/news/2025/draft-sp-800-227-is-available-for-comment · https://csrc.nist.gov/news/2025/nist-publishes-sp-800-227 · https://csrc.nist.gov/News/2025/control-overlays-for-securing-ai-systems · https://csrc.nist.gov/pubs/ir/8596/iprd · https://csrc.nist.gov/News/2026/ai-data-center-security-analysis-draft-sp-800-239
- EU AI Act: https://artificialintelligenceact.eu/article/12/ · https://artificialintelligenceact.eu/article/19/ · https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai · https://www.lw.com/insights/2026/08/Deciphering-the-EU-AI-Act
- OWASP: https://genai.owasp.org/llm-top-10/ · https://owasp.org/www-project-top-10-for-large-language-model-applications/ · https://genai.owasp.org/initiatives/agentic-security-initiative/ · https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- Agent provenance standards context: https://arxiv.org/abs/2508.02866 (PROV-AGENT) · https://arxiv.org/html/2606.04990v4 (survey) · https://overt.is/OVERT_v1.1_STANDARD.pdf (OVERT)
