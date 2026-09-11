# AegisTrace — Adopted Skills & Agent Capabilities Registry

**Status:** Active registry. Last updated: 2026-09-12.
**Discovery report:** `docs/research/github-skills.md` (full rationale, license verification notes, and rejection reasons).
**Rule:** no build step may fetch skills from the network; adopted skill files are copied into this repo, pinned to an upstream commit, and recorded here. Re-read each upstream LICENSE file before first use (licenses below were observed from repo pages/READMEs).

## Adopted skills

| Name | Repo | Purpose | License | Why adopted | Where used | Limitations | Version / commit pin |
|---|---|---|---|---|---|---|---|
| **impeccable** (principles + audit) | https://github.com/pbakaus/impeccable | AI design language: 1 skill, 23 `/impeccable` commands (craft, critique, audit, polish…), 61-rule deterministic detector CLI, design hooks | Apache-2.0 [per repo README/label — verify LICENSE file at adoption] | Best-in-class frontend-quality gate; deterministic `npx impeccable detect` runs in CI without an LLM; counters "AI slop" patterns in the Next.js UI | `frontend/` design reviews; CI frontend-quality job (detector with JSON output + waivers); `/impeccable audit` during design iteration | Installs via `npx impeccable install` (network) — run at setup only; Rust CLI adds a dev dependency; opinionated aesthetic defaults need a project override doc | Pin at adoption: record `npx impeccable --version` in this table (not yet installed — pending frontend setup) |
| **taste-skill** (principles only) | https://github.com/Leonxlnx/taste-skill | Anti-slop design taste: DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY dials, typography/spacing guidance | MIT ("Copyright (c) 2026 Leonxlnx") [per README/label — verify] | The three-dial model is a cheap, effective way to constrain generated UI to AegisTrace's restrained enterprise aesthetic | Principles copied into an internal `frontend` skill (AegisTrace-authored SKILL.md, crediting taste-skill); v2 is experimental — take principles, not files | v2 experimental; fast-moving repo (32 open PRs); overlapping scope with impeccable (impeccable is primary) | Adopted: principles only; upstream commit pin recorded at adoption time |
| **animate** (emilkowalski) | https://github.com/emilkowalski/skills | Builds animations from scratch: correct curve/duration/properties | MIT [per README/label — verify] | Graph UI needs correct motion (trust-state transitions, graph diff animations); author is a recognized UI-motion expert (Vercel/Linear) | `frontend/` — copied SKILL.md into `.agents/skills/animate/` | Assumes React/web stack (fits); animation opinions may need trimming for data-dense dashboards | Pin: copy SKILL.md at a recorded commit (not yet copied) |
| **review-animations** (emilkowalski) | https://github.com/emilkowalski/skills | Strict animation reviews against the author's rules | MIT [per README/label — verify] | Pair with `animate` as the review gate for motion work | `frontend/` code-review checklist; `.agents/skills/review-animations/` | Opinionated; some rules may conflict with impeccable — resolve conflicts in favor of impeccable | Pin: same commit as `animate` |
| **pick-ui-library** (emilkowalski) | https://github.com/emilkowalski/skills | Makes the agent choose trusted UI libraries over hand-rolling or abandoned packages | MIT [per README/label — verify] | Matches AegisTrace dependency-hygiene policy (supply-chain company should not ship shady UI deps) | `frontend/` library-selection decisions; `.agents/skills/` | US-centric library recommendations; cross-check against our own vetting list | Pin: same commit as `animate` |
| **react-best-practices** (Vercel) | https://github.com/vercel-labs/agent-skills (skills/react-best-practices) | 40+ React/Next.js performance rules in 8 impact-ranked categories (waterfalls, bundle size, server-side perf, re-renders…) | MIT [per repo README/label — verify] | Official Vercel engineering guidance for the Next.js frontend; directly improves render/data-fetch quality | `frontend/` reviews + `.agents/skills/react-best-practices/` | Rules drift with Next.js majors; no security coverage (performance only). Note: repo has no "next-best-practices" skill — this is the correct name | Pin: record commit at copy time |
| **hallmark** (slop-test gates) | https://github.com/nutlope/hallmark | Design skill with 21 themes, 57 slop-test gates, pre-emit self-critique; Build/Audit/Redesign/Study verbs | MIT [per README — "MIT. Use it, fork it, ship it" — verify] | The slop-test gate list is the best published checklist for "does this UI look AI-generated"; `Study` verb can extract a design DNA from a reference AegisTrace design | Frontend review checklist (hallmark `Audit` as a secondary layer under impeccable's `audit`); NOT installed as primary design system | Overlaps with impeccable (kept secondary on purpose); theme system not adopted (AegisTrace has its own visual language) | Principles adopted; commit pin at adoption time |
| **trailofbits/static-analysis** (external reference) | https://github.com/trailofbits/skills (plugins/static-analysis) | CodeQL/Semgrep/SARIF static-analysis toolkit guidance; related: semgrep-rule-creator | **CC-BY-SA-4.0** (observed) — share-alike content license | Security-firm guidance for backend threat-modeling and Semgrep rule authoring | Used as an external reference during backend security reviews; **not vendored** (CC-BY-SA share-alike is incompatible with copying into a proprietary repo without triggering share-alike on derivative content) | License friction; Claude Code plugin packaging (not portable as-is) | External reference; record upstream version at each use |
| **awesome-agent-skills** (index) | https://github.com/VoltAgent/awesome-agent-skills | Curated discovery index of 1,497+ official/community skills | MIT (index) | Discovery for future adoption (FastAPI/Postgres/threat-modeling skills) | Quarterly re-scan task; source of the additional candidates in `docs/research/github-skills.md` §2 | Index quality varies by maintainer; verify every linked skill's license individually | Bookmark; re-scan logged in this file's history |

## Rejected (with reasons)

| Candidate | Repo | Reason |
|---|---|---|
| write-swift (emilkowalski) | https://github.com/emilkowalski/skills | Swift is not in the AegisTrace stack |
| animate-expo (emilkowalski) | https://github.com/emilkowalski/skills | React Native/Expo not in stack (Next.js frontend) |
| ask-sonner (emilkowalski) | https://github.com/emilkowalski/skills | Library-specific to Sonner; only adopt if Sonner is chosen as the toast library |
| hallmark as primary design system | https://github.com/nutlope/hallmark | Superseded by impeccable as primary (one design system to avoid conflicting guidance) |
| tinaa/other slop-checkers | — | Only candidates with observed license + maintenance evidence were shortlisted |

## Gaps / planned internal skills

- **No quality FastAPI skill found** in observed indexes (checked VoltAgent index + searches, 2026-09-12) — write an internal `aegis-backend` SKILL.md (FastAPI/SQLAlchemy/Postgres patterns) rather than adopting a low-quality external one. [OBSERVED absence — re-verify before finalizing]
- **No quality graph-visualization skill found** — write an internal `aegis-graph-ui` skill (ReactFlow/Cytoscape patterns for provenance-graph rendering: edge semantics, trust-color encoding, expected-vs-observed diff views).
- **Plan an internal `aegis-attackbench` skill** encoding AttackBench scenario authoring rules (so new attack fixtures follow a consistent schema), using `anthropics/skill-creator` guidance as the format reference (license to be verified).
- **Plan an internal `threat-modeling` skill** for STRIDE-per-interaction on MCP/tool boundaries, informed by OWASP Agentic Security Initiative taxonomy (https://genai.owasp.org/initiatives/agentic-security-initiative/).

## Maintenance policy

1. Quarterly: re-scan the VoltAgent index and the discovery report for new candidates; log decisions here.
2. Any adopted file must carry: upstream URL, commit hash, license text reference, and a "copied from" header in the file itself.
3. License re-verification required whenever an upstream repo changes its LICENSE.
