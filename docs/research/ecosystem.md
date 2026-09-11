# AegisTrace — Ecosystem Survey

**Status:** Research deliverable (prior-art + standards workstream)
**Date of research:** 2026-09-12
**Claim tags:** `[DOCUMENTED-BY-SOURCE]` (verified against linked source during this research), `[OBSERVED]` (directly observed page/repo content), `[HYPOTHESIS]`. Unverifiable items are marked **UNVERIFIED**.

> Reading guide: "Provenance runtime?" = does it capture/runtime-analyze causal provenance of executions; "Execution-level trust?" = does it compute trust/integrity for a specific execution/output; "Deviation detection?" = expected-vs-observed behavior comparison. The last column is maturity as observed in Sept 2026 (stars/funding/market presence), not a quality judgment.

---

## 1. Master comparison table

| Project / product | What it does | Provenance runtime? | Execution-level trust? | Deviation detection? | License | Maturity |
|---|---|---|---|---|---|---|
| **SLSA** | Build-security levels + provenance format [D: slsa.dev/spec/v1.2/] | No (build-time) | No | No | Community Spec License 1.0 [D] | Industry standard, v1.2 current [O] |
| **in-toto (+ Attestation Framework)** | Software supply-chain layout + attestation statements [D: github.com/in-toto/attestation] | No (build/deploy-time) | No | No | Apache-2.0 [O] | CNCF graduated [D: in-toto.io] |
| **Sigstore / Cosign** | Keyless artifact signing: Fulcio OIDC certs, Rekor log [D: docs.sigstore.dev/cosign/signing/overview/] | No | Signature-only (no behavioral trust) | No | Apache-2.0 [O] | GA, widely deployed [D: blog.sigstore.dev/cosign-2-0-released/] |
| **Witness (in-toto/Witness, TestifySec)** | Pluggable framework that "automates, normalizes and verifies software artifact provenance" via attestations + policy [D: github.com/in-toto/witness] | No (build-time attestation) | Policy verdicts on artifacts | Policy-based, build-time only | Apache-2.0 [D: witness.dev / repo — UNVERIFIED exact file this session] | OSS, backed by TestifySec commercial platform [D: testifysec.com] |
| **SPDX 3.0** | SBOM standard; AI + Dataset profiles [D: fossa.com/blog/spdx-3-0/] | No | No | No | SPDX license (LF) [O] | 3.0.1 current [O] |
| **CycloneDX 1.6** | SBOM incl. ML-BOM: modelCard, datasets, algorithmic components [D: cyclonedx.org/capabilities/mlbom/] | No | No | No | Apache-2.0 (spec repo); ECMA-424 [D] | v1.6 current; 1.5→1.6 added AI/ML + CBOM [D: reversinglabs.com/blog/cyclonedx-16-...] |
| **OpenTelemetry GenAI semconv** | Telemetry naming for LLM/agent spans, metrics, events [D: opentelemetry.io/docs/specs/semconv/gen-ai/] | Partial (observability traces, not security provenance) | No | No | Apache-2.0 [O] | Moved to dedicated repo `semantic-conventions-genai`; Development status [D] |
| **MLflow** | Experiment tracking + model registry + LLM tracing [D: mlflow.org] | No (lineage of models, not runtime executions) | No | No | Apache-2.0 [D: mlflow.org/arize-phoenix-alternative] | Very widely adopted |
| **LangSmith** | LLM/agent observability, evals, prompt management [D: openobserve.ai/blog/langsmith-alternatives/ describes as closed-source] | Traces, not security provenance | No | Evals ≠ deviation detection | Closed source [D: openobserve.ai, morphllm.com] | Commercial leader (LangChain) |
| **Langfuse** | OSS LLM/agent observability + evals [D: langfuse.com] | Traces, not security provenance | No | No | MIT core [D: langfuse.com/resources/engineering/best-phoenix-arize-alternatives] | Popular OSS; EE tier |
| **Arize Phoenix** | OTEL-native LLM tracing/evals [D: arize.com/docs/phoenix] | Traces, not security provenance | No | No | **Elastic License 2.0 (ELv2)** — source-available, no hosted resale [D: arize.com/docs/phoenix/self-hosting/license] | Popular OSS-adjacent |
| **W&B Weave** | LLM tracing/eval/monitoring SDK+platform [D: respan.ai/market-map/compare/mlflow-vs-weights-and-biases] | Traces | No | No | Weave SDK Apache-2.0; platform commercial [D: spheron.network/blog/weights-biases-pricing-vs-self-hosted-mlflow-2026] | Commercial |
| **Cisco AI Defense** (ex-Robust Intelligence) | End-to-end AI security: model/app/usage protection [D: cisco.com/.../robust-intelligence-is-part-of-cisco/] | No public evidence of causal provenance graphs | Guardrail verdicts | Runtime guards, not expected-vs-observed graphs | Proprietary | Acquired Oct 2024; AI Defense launched Jan 2025 [D] |
| **Palo Alto Prisma AIRS + Protect AI** | AI lifecycle security: scanning, LLM security, red teaming [D: paloaltonetworks.com/company/press/2025/palo-alto-networks-completes-acquisition-of-protect-ai] | Partial: Protect AI Guardian does ML pipeline security scanning; no public causal-graph runtime proof | Scanning verdicts | No | Proprietary | Protect AI deal closed Jul 22, 2025 (~$650–700M) [D] |
| **Check Point + Lakera** | AI-native guard for LLM apps (Lakera Guard/Red) [D: checkpoint.com/press-releases/check-point-acquires-lakera-...] | No | Guard verdicts | Prompt/response content detection, not graph deviation | Proprietary | Acquisition announced Sept 16, 2025 (~$300M) [D] |
| **SentinelOne + Prompt Security** | Runtime security for GenAI/agentic AI [D: prompt.security; acquisition coverage] | Positioning mentions runtime for GenAI; no public causal provenance graph | Guard verdicts | Content/behavior heuristics | Proprietary | Acquired Jul 2, 2025 (~$250M) [D] |
| **HiddenLayer** | Model scanner / AI threat detection (model file malware, adversarial ML) [HYPOTHESIS positioning; company verified as AI security vendor — details UNVERIFIED this session] | No public evidence | Scanner verdicts | Model-file anomalies | Proprietary | Active vendor (see market maps) [D: prompt.security/ai-security-startup-map] |
| **CalypsoAI** | AI guardrails/red-teaming for enterprises [D: f5.com/.../f5-to-acquire-calypsoai-...] | No | Guard verdicts | No | Proprietary | Acquired by F5, Sept 2025 (~$180M) [D] |
| **Lasso Security** | AI security platform; visibility/control across models, agents, apps; MCP Gateway [D: lasso.security] | Gateway-level policy; no causal provenance graph | Policy verdicts | Gateway rules | Proprietary | $36M raised (per search results) [D] |
| **Knostic** | "Need-to-know" LLM data access (anti-oversharing) [D: knostic.ai/blog/ending-llm-oversharing-...] | No | No | No | Proprietary | $11M round (Mar 2025) [D] |
| **Zenity** | Security/governance for AI agents, "buildtime to runtime" [D: zenity.io] | Agent-inventory + policy; no public causal execution graphs | Policy verdicts | Behavioral anomaly detection claims [HYPOTHESIS — marketing language] | Proprietary | $125M Series C (2026) [D] |
| **Aim Security** | AI/agent security (SASE-integrated) [D: catonetworks.com/news/cato-acquires-aim-security-...] | No public evidence | No | No | Proprietary | Acquired by Cato Networks Sept 3, 2025 [D] |
| **Invariant Labs (→ Snyk)** | Agent security research; **mcp-scan** (MCP tool-poisoning/prompt-injection scanner); trace explorer + guardrails [D: invariantlabs.ai/blog; snyk/agent-scan] | **Trace analysis (Invariant Explorer)** — retrospective trace inspection, not expected-vs-observed verification | Scan findings | Scanner/static + trace review | OSS scanner (mcp-scan); company proprietary | **Acquired by Snyk June 24, 2025** (NOT Anthropic) [D: invariantlabs.ai; snyk/agent-scan on GitHub] |
| **Cisco AI Defense** (agent angle) | see above | — | — | — | — | — |
| **Pangea (→ CrowdStrike)** | AI security services (guard, redaction) [D: search results re CrowdStrike acquisition week of Lakera deal] | No | Service verdicts | No | Proprietary | Acquired by CrowdStrike, Sept 2025 [D] |
| **model-transparency (Sigstore)** | Signs ML models via Sigstore; signatures stored in transparency log [D: github.com/sigstore/model-transparency; blog.sigstore.dev/model-transparency-v1.0/] | No | Integrity of model artifact only | No | Apache-2.0 [O] | v1.x; OpenSSF **Model Signing (OMS) spec** (June 2025), `model-signing` on PyPI [D: openssf.org/blog/2025/06/25/an-introduction-to-the-openssf-model-signing-oms-specification/] |
| **Hugging Face malware scanning** | Scans models on the Hub (pickle/unsafe formats) [HYPOTHESIS on mechanism; the Hub's security scanning including ActiveFence partnership is documented in HF blog posts — UNVERIFIED this session] | No | Scan verdicts | No | Service-side | Live at scale [O] |
| **Falco** (CNCF) | Runtime threat detection from syscalls via rules [D: falco.org — UNVERIFIED this session] | Syscall event streams, not causal provenance graphs | Rule verdicts | Rule-based anomalies | Apache-2.0 [HYPOTHESIS — verify] | CNCF, mature |
| **Tracee (Aqua)** | eBPF runtime security + event tracing [D: github.com/aquasecurity/tracee — UNVERIFIED this session] | Rich syscall observability | No | Detection policies | Apache-2.0 [HYPOTHESIS] | OSS, active |
| **Tetragon (Isovalent/Cisco)** | eBPF-based policy enforcement + observability [D: cilium.io/tetragon — UNVERIFIED this session] | Event-level tracing | Enforcement verdicts | Policy-based | Apache-2.0 [HYPOTHESIS] | Mature |
| **NVIDIA Confidential Computing** | Protects AI models in Hopper/Blackwell/Rubber GPU TEEs without code changes [D: nvidia.com/en-us/data-center/solutions/confidential-computing/] | No (hardware attestation of the machine, not of execution behavior) | Hardware root-of-trust only | No | Proprietary | Hopper→Blackwell→Rubin rollout [D] |
| **Azure Confidential GPU (NCC H100 v5)** | Confidential VMs with H100 (AMD SEV-SNP + H100 NVL), GA Oct 2024 [D: learn.microsoft.com/.../nccadsh100v5-series; blogs.nvidia.com/.../azure-confidential-vm-h100-general-availability/] | No | HW attestation | No | Proprietary | GA [D] |
| **Google Confidential Space / Confidential VMs + GPUs** | TEE VMs with GPUs (SEV-SNP + H100); new Blackwell-based confidential offerings [D: cloud.google.com/blog/products/identity-security/verifiable-trust-in-the-ai-era-whats-new-in-confidential-computing; docs.cloud.google.com/confidential-computing/confidential-vm/docs/create-a-confidential-vm-instance-with-gpu] | No | HW attestation | No | Proprietary | Expanding 2025–2026 [D] |
| **PROV-AGENT (Oak Ridge et al., IEEE e-Science 2025)** | Provenance model + near-real-time capture system for agentic workflows; extends W3C PROV + MCP [D: arxiv.org/abs/2508.02866] | **Yes — capture & querying** | No (assessment of hallucination risk, no trust scores) | No | Paper CC BY 4.0; system OSS per paper [D] | Academic prototype |
| **NeuroTaint (arXiv:2604.23374, 2026)** | "First comprehensive taint tracking framework tailored for… LLM agents" [D: arxiv.org/html/2604.23374v1] | Yes (taint flow) | Labels, not certificates | No | Paper | Preprint |
| **From Agent Traces to Trust — survey (arXiv:2606.04990, Jun 2026)** | Systematic review of evidence tracing & execution provenance in LLM agents; names gap in recovery/invalidation [D: arxiv.org/html/2606.04990v4] | (survey) | (survey) | (survey) | Paper | Survey, Jun 2026 |
| **Who&When (ICML 2025)** | Benchmark + methods for attributing multi-agent failures to the agent and step [D: arxiv.org/abs/2505.00212] | Post-hoc analysis of logs | No | Post-hoc failure attribution | Benchmark dataset (HF) | ICML 2025 Spotlight [D] |
| **AgentAuditor (NeurIPS 2025)** | Training-free, memory-augmented LLM-agent safety/security evaluation framework [D: arxiv.org/abs/2506.00641] | Evaluation layer over traces | Evaluation scores | Evaluation-based | Academic | NeurIPS 2025 [D] |
| **AgentSign (community, agentsign.dev)** | Zero-trust identity + signing for AI agents: identity certs, signed execution chains (DAG of I/O hashes), runtime hash attestation, output tamper detection, trust scoring [D: news.ycombinator.com/item?id=47325206] | **Partial — signed DAG of execution I/O** | **Yes — cryptographic trust scoring** | **Partial — tamper/replay detection, no behavioral expected-vs-observed graphs** | UNVERIFIED (repo github.com/razashariff/agentsign-sdk; claims "patent pending") | Solo/community project; heavily criticized on HN for hash-only attestation limits [D: HN thread] |
| **OVERT (overt.is)** | "Open Standard for Runtime Trust in AI Systems" v1.1 — incl. MCP server runtime attestation requirements [D: overt.is/OVERT_v1.1_STANDARD.pdf] | Requirements-level | Requirements-level | Requirements-level | Standard doc [O] | Community standard; adoption UNVERIFIED |
| **TRACE (OPAQUE, AMD, Intel, TII)** | "Trust, Runtime Attestation and Compliance Evidence" open standard for AI [D: surfaced in search results; primary page UNVERIFIED] | TEE-flavored attestation | Attestation evidence | No | Standard | Announced; maturity UNVERIFIED |

Legend: D = [DOCUMENTED-BY-SOURCE], O = [OBSERVED]. Full URLs in the section bodies below.

---

## 2. Provenance & attestation standards layer

- **SLSA v1.2** — current version; adds Source Track over v1.1's Build Track; provenance/VSA are recommended (not required) formats. https://slsa.dev/spec/v1.2/ [O], https://slsa.dev/spec/v1.2/whats-new [D].
- **in-toto attestation framework** — spec v1, DSSE statements, vetted predicates, Go/Python/Rust/Java bindings. https://github.com/in-toto/attestation [O]. ITE-6 (contextual attestations) accepted; ITE-7 (X.509) draft; ITE-9 (new attestation types) accepted; ITE-8 not listed. https://github.com/in-toto/ITE [O].
- **Sigstore** — GA; keyless signing via Fulcio/Rekor/OIDC. https://docs.sigstore.dev/cosign/signing/overview/ [D].
- **Witness** — in-toto implementation for generating/verifying attestations with policy; commercialized by TestifySec ("turns every build into cryptographically signed, audit-ready evidence"). https://github.com/in-toto/witness [O], https://www.testifysec.com/ [D].
  - Note: the project brief's "Siberas" enterprise angle could **not** be verified — no company named Siberas found in searches; treat as **UNVERIFIED**.
- **What none of them do** [HYPOTHESIS grounded in observed scope]: runtime execution graphs of AI systems, expected-vs-observed comparison, trust propagation, output invalidation.

## 3. BOM / transparency formats

- **SPDX 3.0** (Apr 2024; 3.0.1 Dec 2024): AI + Dataset profiles. https://fossa.com/blog/spdx-3-0/ [D].
- **CycloneDX 1.6 / ECMA-424**: ML-BOM with modelCard/datasets/algorithmic components; CBOM added in 1.6. https://cyclonedx.org/capabilities/mlbom/ [D], https://github.com/cyclonedx/specification [O].
- **Gap:** BOMs are inventories; they have no runtime or causal semantics. The CycloneDX "Authoritative Guide to AI/ML-BOM" (First Edition Rev 1) exists as a PDF guide [O].

## 4. Observability & registries

- **OpenTelemetry GenAI**: conventions moved to https://github.com/open-telemetry/semantic-conventions-genai [D]; agent/framework span doc: `docs/gen-ai/gen-ai-agent-spans.md` [D]; still Development/Experimental status [D].
- **MLflow** (Apache-2.0): model registry + LLM tracing; positions itself vs Phoenix. https://mlflow.org/arize-phoenix-alternative [D].
- **LangSmith**: closed-source commercial LLM observability [D: openobserve.ai/blog/langsmith-alternatives/]. **Langfuse**: MIT-licensed OSS alternative on ClickHouse [D: langfuse.com/resources/engineering/best-phoenix-arize-alternatives]. **Arize Phoenix**: OTEL-native, **ELv2** license [D: arize.com/docs/phoenix/self-hosting/license]. **W&B Weave**: SDK Apache-2.0, platform commercial (~$25k/yr cited in one comparison — secondary source [D: spheron.network/blog/weights-biases-pricing-vs-self-hosted-mlflow-2026]).
- **Gap:** all produce *traces* (what happened) but none produce *attested, signed, causal trust conclusions* (was what happened trustworthy, and which outputs are affected). Traces are also mutable/unauthenticated by default [HYPOTHESIS].

## 5. AI security platforms (guardrails / model security)

2024–2026 was a consolidation wave [D: acquisitions below]:
- **Cisco ← Robust Intelligence** (announced Aug 2024, closed Oct 2024) → **Cisco AI Defense** launched Jan 2025. https://www.cisco.com/site/us/en/products/security/ai-defense/robust-intelligence-is-part-of-cisco/index.html [D].
- **Palo Alto Networks ← Protect AI** (closed Jul 22, 2025; ~$650–700M) → folded into **Prisma AIRS**. https://www.paloaltonetworks.com/company/press/2025/palo-alto-networks-completes-acquisition-of-protect-ai [D].
- **Check Point ← Lakera** (announced Sept 16, 2025; ~$300M reported). https://www.checkpoint.com/press-releases/check-point-acquires-lakera-to-deliver-end-to-end-ai-security-for-enterprises/ [D].
- **SentinelOne ← Prompt Security** (Jul 2, 2025; ~$250M reported). https://prompt.security [D].
- **F5 ← CalypsoAI** (Sept 2025; ~$180M). https://www.f5.com/company/news/press-releases/f5-to-acquire-calypsoai-to-bring-advanced-ai-guardrails-to-large-enterprises [D].
- **Cato Networks ← Aim Security** (Sept 3, 2025; first Cato acquisition). https://www.catonetworks.com/news/cato-acquires-aim-security-to-extend-sase-leadership-and-secure-enterprise-ai-transformation/ [D].
- **CrowdStrike ← Pangea** (Sept 2025, same week as the Lakera deal — per search-result coverage [D]).
- **HiddenLayer** — model-threat detection vendor; included in the Prompt Security "AI Security Startup Map" (406 companies tracked) https://prompt.security/ai-security-startup-map [O]; specific product claims **UNVERIFIED this session**.
- **Knostic** — "need-to-know" access control for LLMs/Copilot; $11M raise Mar 2025. https://www.knostic.ai/blog/ending-llm-oversharing-we-raised-11-million-to-secure-enterprise-ai [D].
- **Zenity** — "security and governance from buildtime to runtime" for AI agents; $125M Series C. https://zenity.io/ [D].
- **Lasso Security** — enterprise AI security incl. MCP gateway; $36M raised. https://www.lasso.security/ [D].
- **Knostic/Lasso/Witness (enterprise angle):** the enterprise demand signaled by TestifySec's compliance mapping (NIST 800-53, FedRAMP, SOC 2) shows attestations are being sold as audit evidence — evidence AegisTrace can reuse in GTM. https://www.testifysec.com/ [D].
- **Market sizing (secondary):** agentic AI security market projected $1.65B (2026) → $13.52B (2032) per MarketsandMarkets, as quoted in search-result coverage [D — secondary].
- **Gap:** all of these are *content/behavior guards and scanners*. None publish a **causal provenance graph of an execution**, compare it to an **expected graph**, or **invalidate downstream outputs** when a dependency is later found compromised [HYPOTHESIS — based on public positioning reviewed this session].

## 6. Agent security startups

- **Invariant Labs** (ETH Zurich spin-off) — agent security research; **mcp-scan** open-source scanner for MCP tool poisoning/prompt injection; "Invariant Explorer" trace analysis; **acquired by Snyk on June 24, 2025** (corrects the project brief's "acquired by Anthropic?" — no Anthropic acquisition found). Successor OSS: **snyk/agent-scan** ("Discover and scan agent components… agents, MCP servers, skills"). https://invariantlabs.ai/blog [D], https://github.com/snyk/agent-scan [O].
- **Zenity** — see §5. **Lasso** — MCP Gateway (see §5). **Aim Security** — acquired by Cato (see §5).
- **Gap:** these tools scan *configurations and traces*; none verify that an *execution* matched an *expected causal plan*, nor propagate trust through the causal graph [HYPOTHESIS].

## 7. Supply-chain security for ML

- **sigstore/model-transparency** — "Supply chain security for ML… protect the integrity of a model by signing it," signatures via Sigstore, recorded in a transparency log. https://github.com/sigstore/model-transparency [O]; announcement: https://blog.sigstore.dev/model-transparency-v1.0/ [D]. Red Hat applied it to model authenticity: https://next.redhat.com/2025/04/10/model-authenticity-and-transparency-with-sigstore/ [D].
- **OpenSSF Model Signing (OMS) specification** (introduced June 25, 2025); `model-signing` on PyPI. https://openssf.org/blog/2025/06/25/an-introduction-to-the-openssf-model-signing-oms-specification/ [D].
- **Hugging Face malware scanning** — Hub-side scanning of model repos (incl. the ActiveFence partnership) [HYPOTHESIS for details; the capability exists on the Hub — UNVERIFIED this session].
- **Protect AI Guardian** — AI/ML pipeline security scanning (now part of Palo Alto). [D: PANW press release above; feature details UNVERIFIED this session.]
- **Gap:** model signing covers *artifacts at rest/in transit*. It says nothing about what the model *does* in an execution, nor about tools/retrieval/MCP at runtime [HYPOTHESIS].

## 8. Runtime security (eBPF lineage)

- **Falco** (CNCF): syscall-based runtime threat detection with rules. **Tracee** (Aqua): eBPF event tracing. **Tetragon** (Isovalent/Cisco): eBPF policy enforcement. Canonical sites: falco.org, github.com/aquasecurity/tracee, cilium.io/tetragon [UNVERIFIED this session — well-known; verify before citing in public docs].
- **Relevance:** these prove host-level provenance capture at scale is feasible, and a Falco-style rules model is a useful contrast: rules over syscalls vs. AegisTrace's semantic graphs over AI abstractions [HYPOTHESIS].
- Classic research lineage (BackTracker, PASIS/SITAR-era, Wang & Stolfo lineage work, HOLMES/NoDoze/RapSheet) is covered in **prior-art.md**.

## 9. TEE / confidential computing for AI

- **NVIDIA Confidential Computing**: protects models on Hopper/Blackwell/Rubin GPUs "without code changes." https://www.nvidia.com/en-us/data-center/solutions/confidential-computing/ [D]; H100 CC-mode technical overview: https://developer.nvidia.com/blog/confidential-computing-on-h100-gpus-for-secure-and-trustworthy-ai/ [D].
- **Azure Confidential GPU**: NCC H100 v5 (AMD SEV-SNP + H100 NVL), GA Oct 2024. https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nccadsh100v5-series [D]; https://blogs.nvidia.com/blog/azure-confidential-vm-h100-general-availability/ [D].
- **Google Cloud**: Confidential VMs with GPUs (SEV-SNP + H100): https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/create-a-confidential-vm-instance-with-gpu [D]; 2025–2026 expansion incl. Blackwell-based Confidential G4 VMs: https://cloud.google.com/blog/products/identity-security/verifiable-trust-in-the-ai-era-whats-new-in-confidential-computing [D].
- **Relationship to AegisTrace:** TEEs attest *the hardware/measurements of the machine*; AegisTrace attests *the causal behavior of the AI workload*. Complementary layers: a TEE-protected execution is still free to call a poisoned MCP server or follow an injected instruction — behavior deviation remains invisible to hardware attestation [HYPOTHESIS]. Note the community **TRACE** standard (OPAQUE/AMD/Intel/TII) is attempting to bridge attestation evidence into AI compliance [D via search results; primary source UNVERIFIED].

## 10. Academic & community — agent provenance (fast-moving)

- **PROV-AGENT** (IEEE e-Science 2025; Oak Ridge-led): provenance model + near-real-time capture for agentic workflows, extending W3C PROV and MCP; evaluated across edge/cloud/HPC. Explicitly does **not** include deviation detection, trust propagation, output invalidation, or quarantine per its abstract. https://arxiv.org/abs/2508.02866 [D].
- **NeuroTaint** (arXiv:2604.23374, 2026): taint tracking tailored to LLM-agent information flows. https://arxiv.org/html/2604.23374v1 [D].
- **Survey: "From Agent Traces to Trust" (arXiv:2606.04990, v4 Jun 2026)**: taxonomy of trace sources, evidence vs execution units, provenance relations (incl. **Invalidate**), and trust functions; identifies gaps exactly adjacent to AegisTrace: "systems detect unsafe behavior but rarely use provenance to invalidate stale memory, quarantine contaminated evidence…"; notes execution-provenance metrics (trace completeness, dependency coverage) are still just "Proposed" desiderata. https://arxiv.org/html/2606.04990v4 [D].
- **Who&When** (ICML 2025 Spotlight): failure attribution benchmark for multi-agent systems ("Which agent causes task failures and when"), 127 systems, best method 53.5% step-level accuracy. https://arxiv.org/abs/2505.00212 [D].
- **AgentAuditor** (NeurIPS 2025): training-free safety/security evaluation for LLM agents. https://arxiv.org/abs/2506.00641 [D].
- **awesome-agent-runtime-security** (curated list incl. taint-tracking references): https://github.com/bureado/awesome-agent-runtime-security [O].
- **OVERT** — community "Open Standard for Runtime Trust in AI Systems" v1.1 incl. MCP server runtime attestation requirements. https://overt.is/OVERT_v1.1_STANDARD.pdf [O].
- **AgentSign** — community project (agentsign.dev; SDK at github.com/razashariff/agentsign-sdk) claiming identity certs + signed execution chains + hash-based runtime attestation + output tamper detection + cryptographic trust scoring; "patent pending" claim on HN; discussion raised fundamental limits of hash-only attestation. https://news.ycombinator.com/item?id=47325206 [O]. **This is the closest community prior art to AegisTrace's thesis — see prior-art.md.**

---

## 11. Ecosystem conclusions

1. **Standards layer is mature and reusable**: SLSA/in-toto/Sigstore/DSSE give AegisTrace free signing/attestation infrastructure; CycloneDX 1.6 and SPDX 3.0 give it BOM interoperability; OTEL GenAI gives it an observation vocabulary [D/O evidence above].
2. **The guardrail/security market consolidated into platform vendors in 2024–2026** (Cisco, PANW, Check Point, SentinelOne, F5, Cato, CrowdStrike) — all focused on content/behavior guarding and scanning; none demonstrated runtime causal provenance with expected-vs-observed verification in public materials reviewed [HYPOTHESIS based on D sources].
3. **The academic agent-provenance wave is 12–18 months old** (PROV-AGENT Aug 2025; NeuroTaint 2026; survey Jun 2026) and already names AegisTrace's target features (invalidation, quarantine, dependency coverage metrics) as open gaps — good news for novelty, bad news for a long head start [D].
4. **Community standards (OVERT, TRACE) and solo projects (AgentSign) show demand** for exactly AegisTrace's positioning ("runtime trust for AI"), which validates the problem but also signals the white space is being noticed [D/O].
