# AegisTrace — Agent Skills Discovery Report

**Status:** Research deliverable (skills workstream)
**Date of research:** 2026-09-12
**Claim tags:** `[OBSERVED]` = directly observed on the linked GitHub repo page during this research (README + license badge/label). Where only a README statement (not the LICENSE file bytes) confirmed the license, that is noted. **UNVERIFIED** where applicable.
**Companion registry:** `docs/SKILLS.md` (the actionable adopt/reject table).

> Method: each candidate repo was inspected via its GitHub page (README, license label, stats: stars/forks/commits/issues/PRs). No files were downloaded or installed. License identifiers below come from the repo's license label / README statements observed on the fetched page; before vendoring any skill file, re-read the LICENSE file directly (one-line verification task).

---

## 1. Candidate repos (as requested)

### 1.1 pbakaus/impeccable — design-quality skill suite

- **Repo:** https://github.com/pbakaus/impeccable [OBSERVED]
- **Purpose:** "The design language that makes your AI harness better at design" — descends from Anthropic's frontend-design skill; targets "AI slop" (Inter everywhere, purple-blue gradients, nested cards, gray-on-color text). Ships **1 skill, 23 commands** (`/impeccable craft|critique|audit|polish|bolder|quieter|distill|harden|animate|live`...), a **detector CLI** (`npx impeccable detect`) with **61 deterministic rules** (no LLM/API key needed; JSON output, exit codes, waiver comments — CI-friendly), a design hook for Claude Code/Cursor/Codex/Copilot/Grok Build, and live browser iteration. [OBSERVED]
- **License:** Apache-2.0 (README states "Apache 2.0. See LICENSE"; GitHub labels it Apache-2.0). [OBSERVED — README statement; verify LICENSE file before vendoring]
- **Stats:** ~67.3k stars, 4.1k forks, 1,863 commits, 16 open issues, 8 open PRs. Docs at impeccable.style. [OBSERVED]
- **Why adopt for AegisTrace:** (a) the `/impeccable audit` + `critique` workflow directly improves the Next.js frontend's visual quality; (b) the deterministic detector can run in CI as a frontend quality gate — this matches AegisTrace's engineering culture (deterministic checks over vibes); (c) Apache-2.0 is compatible with a proprietary core. [HYPOTHESIS → decision: ADOPT-PRINCIPLES + adopt detector usage]
- **Security/maintenance:** very high activity; Rust `crates/` engine; per-harness install folders; from a known maintainer (Paul Bakaus). Supply-chain risk low if pinned; the `npx` installer should be run at setup, not in CI builds. [HYPOTHESIS]
- **Decision: ADOPT-PRINCIPLES** (design language + audit/critique commands for the frontend) — do not vendor wholesale; pin the version via the skills CLI at setup time. [HYPOTHESIS]

### 1.2 Leonxlnx/taste-skill — "anti-slop" design taste skill

- **Repo:** https://github.com/Leonxlnx/taste-skill [OBSERVED]
- **Purpose:** "The Anti-Slop Frontend Framework for AI Agents… gives your AI good taste." Portable SKILL.md files; flagship skill tunes three dials — DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY (1–10); v2 experimental + v1 preserved; variants (gpt-taste, image-to-code, redesign, minimalist, brutalist, soft/premium, full-output-enforcement) plus image-generation skills. Install via `npx skills add https://github.com/Leonxlnx/taste-skill`. [OBSERVED]
- **License:** MIT — "MIT License · Copyright (c) 2026 Leonxlnx" (README/license label). [OBSERVED]
- **Stats:** ~86.3k stars, 5.9k forks, 154 commits, 31 open issues, 32 open PRs; sponsored by Kimi (Moonshot AI), interfaces.dev, others. README explicitly disclaims any crypto token. [OBSERVED]
- **Why adopt:** lightweight principle-level guidance (dials) is easy to AegisTrace-ify (e.g., fix the dials to "restrained enterprise dashboard" values for the trust-graph UI). Why limit: v2 is experimental; 32 open PRs = moving target; overlapping purpose with impeccable (pick one as primary). [HYPOTHESIS]
- **Security/maintenance:** active but fast-moving; single-owner repo; pin a specific commit if any file is copied. [HYPOTHESIS]
- **Decision: ADOPT-PRINCIPLES** (the three-dial model + typography/spacing principles), copied into AegisTrace's own frontend skill rather than installed as a dependency. [HYPOTHESIS]

### 1.3 emilkowalski/skills — animation & UI craft skills

- **Repo:** https://github.com/emilkowalski/skills [OBSERVED]
- **Purpose:** 12 skills "For designers and engineers to help them build better user interfaces," based on the author's experience at Vercel and Linear: `emil-design-eng` (main), `animate`, `animate-expo`, `review-animations`, `improve-animations`, `find-animation-opportunities`, `animation-vocabulary`, `apple-design`, `write-swift` (not relevant), `pick-ui-library`, `prototype`, `ask-sonner`. Install via `npx skills@latest add emilkowalski/skills`. [OBSERVED]
- **License:** MIT (README badge + Resources section). [OBSERVED]
- **Stats:** ~37.0k stars, 2.1k forks, 50 commits, 1 open issue, 0 open PRs (tight, curated). [OBSERVED]
- **Why adopt:** `animate` / `review-animations` / `improve-animations` are directly useful for the Next.js trust-graph UI (animated graph transitions, certificate status changes); `pick-ui-library` matches AegisTrace's dependency-hygiene values; `prototype` helps frontend iteration. `write-swift`, `ask-sonner`, `animate-expo` are not relevant. [HYPOTHESIS]
- **Security/maintenance:** small, stable, low-churn (50 commits), MIT. Low risk. [HYPOTHESIS]
- **Decision: ADOPT-FILE** for `animate` + `review-animations` + `pick-ui-library` (copy SKILL.md files into `.agents/skills/` with commit pin); REJECT `write-swift`, `animate-expo`, `ask-sonner` (not in AegisTrace stack). [HYPOTHESIS]

### 1.4 VoltAgent/awesome-agent-skills — curated directory (discovery, not adoption)

- **Repo:** https://github.com/VoltAgent/awesome-agent-skills [OBSERVED]
- **Purpose:** "A collection of official Agent Skills from leading development teams and the community… Hand-picked, not AI-slop generated," compatible with Claude Code, Codex, Antigravity, Gemini CLI, Cursor, Copilot, OpenCode, Windsurf. Organized by publisher: Anthropic, OpenAI, Microsoft (133 skills), Vercel, Cloudflare, Stripe, Supabase, HashiCorp, Trail of Bits, Sentry, Figma, Hugging Face, Expo, Neon, ClickHouse, etc. Badge counts 1,497+ skills. [OBSERVED]
- **License:** MIT (repo license label). [OBSERVED]
- **Stats:** ~34.1k stars, 3.6k forks, 619 commits. [OBSERVED]
- **Why use:** as the *discovery index* for the second-tier survey below; not itself a skill. [HYPOTHESIS]
- **Decision: REJECT as a skill; ADOPT as an index** (bookmark; re-check quarterly for FastAPI/Postgres/threat-modeling skills). [HYPOTHESIS]

### 1.5 nutlope/hallmark — design skill with slop-test gates

- **Repo:** https://github.com/nutlope/hallmark [OBSERVED]
- **Purpose:** by Together AI (Hassan El Mghari): "A design skill for Claude Code, Cursor, and Codex that refuses to look AI-generated." Picks a layout macrostructure, applies one of **21 themes**, runs **57 slop-test gates plus a pre-emit self-critique**. Verbs: **Build / Audit / Redesign / Study** (Study extracts a portable `design.md` from a design you admire; refuses pixel-clones). Install via `npx skills add nutlope/hallmark`; demo at usehallmark.com. [OBSERVED]
- **License:** MIT ("MIT. Use it, fork it, ship it" per README). [OBSERVED]
- **Stats:** ~28.4k stars, 1.5k forks, 138 commits, 20 open issues, 26 open PRs. [OBSERVED]
- **Why adopt:** `Audit` and `Study` verbs complement impeccable (impeccable = process/critique; hallmark = output gates + design-DNA extraction). The 57 slop-test gates are a good checklist source. Why limit: overlapping with impeccable as the primary design system — use one as primary, the other's audit checklist as a review layer. [HYPOTHESIS]
- **Security/maintenance:** corporate-backed (Together AI), MIT, active. Low risk; pin version. [HYPOTHESIS]
- **Decision: ADOPT-PRINCIPLES** (slop-test checklist + `Audit` verb usage); ADOPT-FILE only if the team prefers hallmark's theme system over impeccable's commands. [HYPOTHESIS]

### 1.6 The 'skills' CLI context (from nutlope/hallmark + VoltAgent)

- The `npx skills add <owner>/<repo>` installer (used by hallmark, taste-skill, vercel-labs, emilkowalski) is the emerging de-facto distribution mechanism for agent skills; it writes into tool-specific locations (`~/.claude/skills/`, `.cursor/rules/`, `~/.codex/skills/`) and supports updates by re-running. [OBSERVED — hallmark README install instructions; emilkowalski + vercel READMEs]
- **AegisTrace posture:** use the CLI at onboarding (documented in README), but **commit copied SKILL.md files into the repo** (with a `SOURCES.md` provenance note — fitting, for a provenance company) so builds never depend on remote skill fetches. [HYPOTHESIS]

---

## 2. Additional high-quality skills surveyed (best 5 for AegisTrace's stack)

| Skill | Repo | Purpose | License | Why relevant |
|---|---|---|---|---|
| **trailofbits/static-analysis** | https://github.com/trailofbits/skills (plugins/static-analysis) | "Static analysis toolkit with CodeQL, Semgrep, and SARIF parsing"; related plugins: c-review, rust-review, semgrep-rule-creator, variant-analysis; from a top security firm; Claude Code plugin marketplace (`/plugin marketplace add trailofbits/skills`) | **CC-BY-SA-4.0** (share-alike — content license, not code license) | Threat-modeling/code-audit support for the FastAPI backend; Semgrep rules for the SDK. **Careful:** CC-BY-SA share-alike means derivative skill *content* must be shared under compatible terms — adopt as an external tool/principles reference rather than vendoring into a proprietary repo. [OBSERVED] |
| **vercel-labs react-best-practices** | https://github.com/vercel-labs/agent-skills (skills/react-best-practices) | "React and Next.js performance optimization guidelines from Vercel Engineering" — 40+ rules across 8 impact-prioritized categories (waterfalls, bundle size, server-side perf, re-renders…) | MIT | Directly applicable to the Next.js frontend. Note: there is **no** skill literally named "next-best-practices" — the correct name is `react-best-practices`. [OBSERVED] |
| **microsoft/mcp-builder** | https://github.com/VoltAgent/awesome-agent-skills (listed under Microsoft) | MCP server creation guidance | UNVERIFIED (listed in the awesome index; check the Microsoft repo) | AegisTrace's SDK ships an MCP integration; a builder skill helps create demo/reference MCP servers for AttackBench fixtures. [OBSERVED as listed] |
| **supabase/postgres-best-practices** | via VoltAgent index | Postgres guidance | UNVERIFIED | Applicable to the PostgreSQL/SQLAlchemy backend layer. [OBSERVED as listed] |
| **anthropics/skill-creator** | https://github.com/anthropics/skills (indexed via VoltAgent) | Guidance for authoring well-structured SKILL.md files | UNVERIFIED | Needed to write AegisTrace's own internal skills (e.g., an `aegis-attackbench` skill, an `expected-graph` design skill) with correct frontmatter/trigger discipline. [OBSERVED as listed] |

**Other categories searched but not adopted:** FastAPI-specific and graph-visualization-specific skills — **none found** in the observed indexes that met a quality bar (no dedicated FastAPI skill surfaced in the VoltAgent index or searches; UNVERIFIED absence — re-search before finalizing). Graph visualization should instead rely on AegisTrace's own ReactFlow/Cytoscape choices — no quality skill found. [OBSERVED/UNVERIFIED]

---

## 3. Summary of decisions

| Item | Decision | Where used |
|---|---|---|
| impeccable (pbakaus) | ADOPT-PRINCIPLES + CI detector usage | frontend design reviews, `/impeccable audit` + `npx impeccable detect` in CI |
| taste-skill (Leonxlnx) | ADOPT-PRINCIPLES (three-dial model) | folded into AegisTrace's own frontend skill |
| emilkowalski/skills | ADOPT-FILE (animate, review-animations, pick-ui-library); REJECT swift/expo/sonner | `.agents/skills/` for frontend work |
| hallmark (nutlope) | ADOPT-PRINCIPLES (slop-test gates, Audit verb) | frontend review checklist |
| VoltAgent/awesome-agent-skills | ADOPT as discovery index (not a skill) | quarterly re-scan |
| trailofbits/static-analysis | ADOPT-PRINCIPLES (external reference; CC-BY-SA caution) | backend security reviews |
| vercel react-best-practices | ADOPT-FILE | Next.js frontend |

The actionable registry lives in **docs/SKILLS.md**.
