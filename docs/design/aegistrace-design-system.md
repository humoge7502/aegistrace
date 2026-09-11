# AegisTrace Design System — "Ledger" v1.0

> **ORIGINAL WORK.** This visual identity, all token names, hex values, and conventions below are original to the AegisTrace project. They were derived from first principles for a security/trust-infrastructure product; they do not copy any third party's branding (see `acm-vit-analysis.md` for the research provenance, which informed *principles only*).
>
> Implementation target: **Tailwind CSS v4** (`@theme` tokens) + **shadcn/ui-style** CSS-variable components + **next/font** (Google Fonts).

---

## 1. Brand concept

### 1.1 Name meaning
- **Aegis** — the shield borne by Zeus and Athena in Greek myth; in modern usage, "under the aegis of" means *under protection and authority*. AegisTrace positions the product as the protective authority over AI execution.
- **Trace** — provenance, lineage, the recorded path of an execution. Also the engineering verb: to trace a causal chain to its origin.
- Together: **"the shield that follows the trace."** Protection that is not a gate at the perimeter, but a witness that follows every execution end-to-end and can *prove* what happened.

### 1.2 Positioning statement
> AegisTrace continuously attests every AI execution, builds a runtime causal provenance graph, and issues a verifiable Trust Certificate for each run — so that enterprises can operate AI systems the way they operate any other governed infrastructure: with evidence, not vibes.

### 1.3 Personality keywords
`Forensic` · `Calm` · `Precise` · `Infrastructural` · `Verifiable` · `Observant` · `Unpresumptuous`

The voice of the UI is a calm incident commander + a meticulous auditor: it states facts, shows evidence, never performs alarmism, never decorates. When something is wrong it says so in plain mono type with a red hairline — it does not flash, it *records*.

### 1.4 What we deliberately avoid
- Generic "AI-startup" aesthetics: purple-to-pink gradients, glowing orbs, floating 3D blobs, "magical sparkle" icons, confetti success states.
- Cyberpunk clichés: matrix rain, neon green terminal-on-black roleplay, scanline overload.
- Dark-pattern urgency: red badges everywhere, alarmist copy, faked "live" numbers.
- Glassmorphism-heavy surfaces and oversized radii (this is an audit tool, not a toy).
- Color as the *only* carrier of meaning (accessibility + graph-density requirement).

### 1.5 Signature elements (the distinctive trio)
1. **The Provenance Rail.** Every application screen carries a 28 px-wide left spine: a vertical hairline with tick marks (like an oscilloscope or legal pad), a live trust-state pulse dot at the top, and timestamp ticks for the active trace. It makes every page feel like part of one continuous record.
2. **Trust Certificate cards.** The "AI Trust Certificate" is rendered as a calibration-certificate-style card: sharp corner with a **notched top-right corner** (`clip-path` cut 10×10 px), a mono serial (`ATC-…`), a hairline double border, and a "verified" stamp treatment (rotated −6°, 1px ring, uppercase mono). No color fills — the state color appears only as a 2 px top edge and the stamp ink.
3. **Deviation edges with marching ants.** In provenance graphs, unexpected causality is drawn as a **dashed red edge with a slow dash-offset animation** (static under reduced motion). This one device makes deviations findable in milliseconds and becomes the product's most recognizable motif.

---

## 2. Color system

Dark-first enterprise theme. All hexes chosen and hand-checked for WCAG contrast (ratios noted). Tailwind v4 `@theme` names given as CSS variables; light theme overrides via `:root[data-theme="light"]` (or `.light` class per shadcn convention).

### 2.1 Neutrals — "Ledger Slate" scale

| Token | Dark | Light | Usage |
|---|---|---|---|
| `--color-bg-deep` | `#070910` | `#EBEEF4` | Graph canvas wells, page background behind app shell |
| `--color-bg` | `#0B0E14` | `#F6F8FB` | App background |
| `--color-surface` | `#11151F` | `#FFFFFF` | Cards, panels, table containers |
| `--color-surface-raised` | `#171C2A` | `#FFFFFF` | Popovers, dropdowns, command palette (dark only raises) |
| `--color-sunken` | `#0D1019` | `#EDF0F5` | Table header rows, code blocks, JSON viewer |
| `--color-border` | `#1E2532` | `#E3E8F0` | Default 1px borders |
| `--color-border-strong` | `#2C3648` | `#CBD4E1` | Hovered/focused borders, table rules |
| `--color-text-primary` | `#E8EDF5` | `#0E1524` | Headings, primary copy (≈15.5:1 / ≈16.8:1) |
| `--color-text-secondary` | `#A9B4C6` | `#3B4759` | Body text (≈8.2:1 / ≈9.6:1) |
| `--color-text-muted` | `#8B95A7` | `#5A6779` | Captions, timestamps (6.4:1 / 5.4:1) |
| `--color-text-faint` | `#667083` | `#8592A5` | Decorative, disabled (3.9:1 — non-text & ≥24px only) |
| `--color-overlay` | `rgba(7,9,16,0.72)` | `rgba(14,21,36,0.40)` | Modal scrims |

### 2.2 Primary accent — "Attestor Cyan" (interactive/brand only)

Cyan/electric-teal on near-black. Deliberately **not** AI-purple. Cyan is reserved for *interactivity and brand chrome* — never for trust states (that keeps state colors unambiguous).

| Token | Hex | Usage / contrast |
|---|---|---|
| `--accent-300` | `#67E8F9` | Dark: JSON keys, link hover, selected node ring |
| `--accent-400` | `#22D3EE` | Dark primary: buttons, links, active tab, focus ring — 10.7:1 on `--color-bg` |
| `--accent-ink` | `#062125` | Text/icons on accent-400 fills — ≈9:1 |
| `--accent-500` | `#06B6D4` | Dark: pressed state, chart accent line |
| `--accent-600` | `#0891B2` | Light UI: buttons, active indicators — 3.7:1 (UI components only) |
| `--accent-700` | `#0E7490` | Light text-on-bg: links — 5.4:1 |
| `--accent-wash` | `rgba(34,211,238,0.08)` | Selected-row wash, hovered icon button (light: `rgba(8,145,178,0.08)`) |
| `--accent-glow` | `0 0 24px rgba(34,211,238,0.16)` | Selected graph node only; never on text |

Light-theme link minimum: use `--accent-700` for text, `--accent-600` only for ≥3:1 non-text elements (borders, fills under dark text).

### 2.3 Trust-state semantic palette (product-wide, reused in UI + graph viz)

Each state defines: `text` (dark theme text/badge label), `text-light` (light theme), `solid` (graph node fill / badge dot / status dot, both themes), `tint` (badge & row washes). All `text` values ≥4.5:1 against their theme bg and their tint backgrounds (light-theme pairs verified against the tint hex; dark-theme text sits on ≤12% tints over `#0B0E14`, headroom >7:1).

| State | `text` (dark) | `text-light` | `solid` | `tint` (dark / light) | Contrast (dark / light) |
|---|---|---|---|---|---|
| **TRUSTED** | `#4ADE80` | `#15803D` | `#22C55E` | `rgba(34,197,94,0.12)` / `#DCFCE7` | 11.1 / 5.0 |
| **UNTRUSTED** | `#F87171` | `#B91C1C` | `#EF4444` | `rgba(239,68,68,0.12)` / `#FEE2E2` | 7.0 / 6.5 |
| **UNKNOWN** | `#94A3B8` | `#475569` | `#94A3B8` | `rgba(148,163,184,0.10)` / `#E2E8F0` | 7.5 / 7.6 |
| **DEGRADED** | `#FBBF24` | `#B45309` | `#F59E0B` | `rgba(245,158,11,0.12)` / `#FEF3C7` | 11.6 / 5.0 |
| **COMPROMISED** | `#FDA4AF` | `#9F1239` | `#E11D48` | `rgba(225,29,72,0.14)` / `#FFE4E6` | 10.2 / 8.0 |
| **QUARANTINED** | `#FB923C` | `#C2410C` | `#F97316` | `rgba(249,115,22,0.12)` / `#FFEDD5` | 8.5 / 5.2 |
| **RECOVERING** | `#60A5FA` | `#1D4ED8` | `#3B82F6` | `rgba(59,130,246,0.12)` / `#DBEAFE` | 7.6 / 6.7 |
| **RE-CERTIFIED** | `#2DD4BF` | `#0F766E` | `#14B8A6` | `rgba(20,184,166,0.12)` / `#CCFBF1` | 10.4 / 5.5 |

Naming map (CSS): `--trust-trusted-text`, `--trust-trusted-text-light`, `--trust-trusted-solid`, `--trust-trusted-tint`, etc.

Disambiguation rules (mandatory):
- **TRUSTED green vs RE-CERTIFIED teal:** trusted is pure green `#22C55E`; re-certified is teal `#14B8A6`. RE-CERTIFIED always appears with a ↻-style "refresh-seal" glyph and, on certificates, a double border.
- **UNTRUSTED vs COMPROMISED:** UNTRUSTED = `#EF4444` *outlined* treatment (red text/border, transparent fill). COMPROMISED = `#E11D48` *filled* treatment (rose solid badge, white text `#FFFFFF` — 4.6:1 on `#E11D48`). Severity is encoded by fill weight, not just hue.
- **Cyan accent vs RE-CERTIFIED teal:** cyan is interactive chrome; teal appears only on state badges/nodes. Never use teal for links or buttons.
- UNKNOWN (`#94A3B8`) doubles as the "no data / disabled" semantic in charts.

### 2.4 Chart & data-viz neutrals

| Token | Dark | Light | Usage |
|---|---|---|---|
| `--viz-grid` | `rgba(154,166,189,0.10)` | `rgba(59,71,89,0.12)` | Dot-grid / axis lines |
| `--viz-edge` | `#3A4560` | `#B9C2D1` | Default graph edges |
| `--viz-edge-verified` | `#56637F` | `#8B95A7` | Attestation-verified edges (slightly stronger) |
| `--viz-series-1..4` | `#22D3EE` `#94A3B8` `#FBBF24` `#8B95A7` | `#0E7490` `#5A6779` `#B45309` `#8592A5` | Time-series only; states use trust palette |

---

## 3. Typography

Two families, both on Google Fonts and available via `next/font/google`:

- **UI & display: IBM Plex Sans** — weights 400/500/600/700. Chosen over trendier geometrics for its engineered, slightly technical voice (it ships with excellent tabular figures).
  `next/font`: `IBM_Plex_Sans({ weight: ['400','500','600','700'], subsets: ['latin'] })`
- **Mono: JetBrains Mono** — weights 400/500/700. For hashes, attestation IDs, digests, timestamps, JSON, certificates, graph edge labels.
  `next/font`: `JetBrains_Mono({ weight: ['400','500','700'], subsets: ['latin'] })`

CSS variables: `--font-sans: var(--font-plex-sans), ui-sans-serif, system-ui, sans-serif;` `--font-mono: var(--font-jetbrains-mono), ui-monospace, monospace;`

### 3.1 Type scale tokens (`@theme` font sizes)

| Token | Size / line-height | Weight | Tracking | Usage |
|---|---|---|---|---|
| `--text-micro` | 11px / 1.2 (0.6875rem) | 500 | `+0.08em`, UPPERCASE | Micro-labels, table column headers, rail ticks |
| `--text-xs` | 12px / 1.45 (0.75rem) | 400 | 0 | Timestamps, captions, badge labels |
| `--text-sm` | 13px / 1.5 (0.8125rem) | 400 | 0 | Secondary UI text, JSON viewer |
| `--text-base` | 14px / 1.55 (0.875rem) | 400 | 0 | App body (enterprise density) |
| `--text-base-relaxed` | 16px / 1.6 (1rem) | 400 | 0 | Marketing/prose mode |
| `--text-lg` | 16px / 1.5 | 500 | 0 | Emphasized UI |
| `--text-xl` | 18px / 1.45 (1.125rem) | 500 | 0 | Card titles, section intros |
| `--text-2xl` | 22px / 1.3 (1.375rem) | 600 | `-0.01em` | Page titles in app |
| `--text-3xl` | 26px / 1.25 (1.625rem) | 600 | `-0.015em` | Dashboard KPIs |
| `--text-4xl` | 32px / 1.2 (2rem) | 600 | `-0.02em` | Marketing h3 |
| `--text-5xl` | 40px / 1.15 (2.5rem) | 700 | `-0.02em` | Marketing h2 |
| `--text-6xl` | 48px / 1.05 (3rem) | 700 | `-0.025em`, UPPERCASE optional | Hero display |
| `--text-hero` | 64px / 1.0 (4rem) | 700 | `-0.03em` | Landing hero (clamp to 40px on mobile) |

### 3.2 Rules
- **ALL-CAPS micro-labels** (`--text-micro`): always with `+0.08em` tracking, never longer than ~30 chars, always sentence-meaningful ("PROVENANCE DEPTH 4", not "AMAZING FEATURES").
- **Mono voice:** every machine-generated string (hash, serial, ID, timestamp, diff) renders in `--font-mono` at 12–13px with `+0.02em` tracking and `font-variant-numeric: tabular-nums`. Never truncate a hash mid-visual without an ellipsis + copy affordance; show first 8 and last 4 chars (`a1b2c3d4…e5f6`).
- Numerals in tables/KPIs: `tabular-nums` always.
- No italics anywhere in the app UI (evidence text must not read as editorial).

---

## 4. Spacing, radius, shadow, border tokens

### 4.1 Spacing (4px base grid)

```
--space-0.5: 2px;  --space-1: 4px;  --space-1.5: 6px; --space-2: 8px;
--space-3: 12px;   --space-4: 16px; --space-5: 20px;  --space-6: 24px;
--space-8: 32px;   --space-10: 40px; --space-12: 48px; --space-16: 64px;
--space-20: 80px;  --space-24: 96px;
```
- App shell gutter: 24px; card padding: 16–20px; table cell padding: 10px 12px; form row gap: 16px.
- Section rhythm (marketing): 96px desktop / 64px mobile. In-app panel rhythm: 24px.
- Density modes: comfortable row height 36px, compact 28px (tables/log streams toggle).

### 4.2 Radius

```
--radius-none: 0; --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px;
--radius-xl: 12px; --radius-pill: 9999px;
--radius-notch: polygon clip — cut 10px × 10px at top-right (certificate cards only)
```
Default surfaces `--radius-lg`. Inputs `--radius-md`. Trust badges `--radius-pill`. Graph popovers `--radius-xl`. Nothing above 12px — the audit-tool restraint line.

### 4.3 Shadows & elevation (borders carry elevation in dark; shadows are subtle)

| Token | Dark | Light |
|---|---|---|
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.50)` | `0 1px 2px rgba(14,21,36,0.08)` |
| `--shadow-sm` | `0 2px 8px rgba(0,0,0,0.45)` | `0 2px 8px rgba(14,21,36,0.08)` |
| `--shadow-md` | `0 8px 24px rgba(0,0,0,0.50)` | `0 8px 24px rgba(14,21,36,0.10)` |
| `--shadow-pop` | `0 12px 32px rgba(0,0,0,0.55), 0 0 0 1px var(--color-border-strong)` | `0 12px 32px rgba(14,21,36,0.14), 0 0 0 1px var(--color-border)` |

Rule: in dark theme, a surface must always be separated from its parent by a **1px border first**, shadow second. Glow (`--accent-glow`) is reserved for selected graph nodes and the live rail pulse — maximum one glowing element per screen.

### 4.4 Borders
- 1px everywhere; 2px only for certificate cards' double-rule and QUARANTINED perimeter fencing.
- Hairline dividers inside a card: `--color-border` at 1px, full-bleed inside the card (no inset margins).

---

## 5. Component conventions

### 5.1 Buttons
| Variant | Dark | Light |
|---|---|---|
| Primary | bg `--accent-400`, text `--accent-ink`, hover bg `--accent-300`, active `--accent-500` | bg `--accent-600`, text `#FFFFFF`, hover `--accent-700` |
| Secondary | bg `--color-surface-raised`, 1px `--color-border-strong`, text primary | bg `#FFFFFF`, border `--color-border-strong` |
| Ghost | transparent, text secondary; hover `--accent-wash` | same with light wash |
| Destructive | bg `--trust-compromised-solid` (`#E11D48`), text `#FFFFFF` | same |
| State (e.g. Quarantine action) | 1px border in the state's `solid`, text in state `text`, transparent bg | same pattern |

Sizes: `sm` h-28px px-10px text-micro; `md` h-34px px-14px text-sm; `lg` h-42px px-18px text-base. Radius `--radius-md`. Icons 16px, 6px gap. Never use state colors for non-state actions.

### 5.2 Cards
- Structure: 1px `--color-border`, `--radius-lg`, bg `--color-surface`, padding 20px; optional 24px `--text-micro` kicker in `--color-text-muted`; trust-state cards add a 2px top edge in the state `solid` and a state badge in the header row.
- Hover (interactive cards): border → `--color-border-strong`, translateY(-1px), `--shadow-sm`. No scale.
- Certificate card: the notched-corner signature (see §1.5); double border via `outline: 1px solid var(--color-border); outline-offset: 3px;` plus the 1px border.

### 5.3 Tables
- Header: `--color-sunken` bg, `--text-micro` uppercase labels, 40px row.
- Rows: 36px (comfortable) / 28px (compact), 1px bottom hairline, no zebra; hover row wash `--accent-wash`; selected row: left 2px `--accent-400` + wash.
- Mono for IDs/hashes/timestamps; `tabular-nums` for all numerics. Sticky header + sticky first column on wide provenance tables.

### 5.4 Badges (trust states)
- Pill, h-20px, px-8px, `--text-xs` 500 weight: 6px state dot (`solid`) + label in state `text` on state `tint`. COMPROMISED uses solid fill + white text (see §2.3).
- Max one badge per row context; in dense logs use the dot alone with `title` + aria-label.

### 5.5 Event timeline
- Vertical rail: 1px `--color-border` at left 8px; each event = 8px state dot on the rail + `--font-mono` 12px timestamp (`HH:MM:SS.mmm`, UTC-suffixed) + 14px text; 12px vertical gap; deviation events draw the dashed-red left segment (the rail echoes the marching-ants motif).
- Live-tailing mode: new events slide in 150ms ease-out; rail pulse dot in `--accent-400` while streaming.

### 5.6 JSON evidence viewer
- Container: `--color-sunken`, `--radius-md`, 1px border, 13px `--font-mono`, line numbers in `--color-text-faint`, gutter 12px.
- Syntax palette (dark / light): keys `#67E8F9` / `#0E7490`; strings `#E8EDF5` / `#0E1524`; numbers `#FBBF24` / `#B45309`; booleans & null `#94A3B8` / `#475569`; punctuation `#667083` / `#8592A5`.
- Hash/ID values get a copy-on-click affordance with a 150ms "copied" tick; foldable nodes (chevron 16px); max-height with internal scroll; "view raw / download .json" in the header row.

### 5.7 Empty / loading / error states
- **Empty:** centered, 40px line-icon in `--color-text-faint`, one-line 14px statement ("No attestations in this window."), one ghost action. Zero marketing copy in empty states.
- **Loading:** skeletons = `--color-sunken` blocks with a 1.6s shimmer sweep (disabled under reduced motion — then a static 40% opacity pulse via two frames). Never spinners on tables; row skeletons only.
- **Error:** banner with `--trust-compromised-tint` bg, 2px left edge `--trust-compromised-solid`, mono error code + human sentence + Retry button. Unknown-cause system failures show UNKNOWN, not red.
- **No attestation / unverifiable:** renders as UNKNOWN gray, explicitly *not* red — absence of evidence is not evidence of compromise.

### 5.8 Focus rings
- `:focus-visible` only: dark `outline: 2px solid var(--accent-400); outline-offset: 2px;` light `var(--accent-700)`. On accent-filled elements: `--color-bg`-colored ring. Never `outline: none` without a visible replacement. Focus is never removed during scroll-lock.

---

## 6. Data-viz & provenance-graph conventions

### 6.1 Entity vocabulary (shape + treatment; color = trust state, never identity)

| Entity | Node shape | Size | Glyph |
|---|---|---|---|
| Model | Circle | 32px | spark/asterisk 12px |
| Agent | Rounded square (squircle, r=8) | 28px | chevron-network |
| Tool | Hexagon | 26px | wrench-less: bracket glyph `[ ]` |
| MCP server | Diamond | 26px | plug/ports glyph |
| Dataset | Cylinder | 26px | stacked-disc lines |
| Document | Rectangle, folded corner | 26px | fold triangle |
| Execution | Double circle (target) | 36px | center dot |
| Output | Rounded rect, dashed border by default | 28px | arrow-out |
| Runtime | Square | 26px | chip pins |
| Package | Ring (annulus) | 24px | hash glyph |

- Fill = trust-state `solid` at 18% opacity, stroke = trust-state `solid` 1.5px; glyph in state `text` (dark theme). Node label: 11px mono, `--color-text-secondary`, below node; deviations add a 2px dashed `#F87171` halo.
- Shape + glyph are mandatory redundancy: state must be readable without color (colorblind-safe by construction).

### 6.2 Edges
- Default causal edge: 1.5px solid `--viz-edge`, arrowhead 6px, label (mono 10px, on demand) e.g. `invoked`, `read`, `emitted`.
- Attestation-verified edge: `--viz-edge-verified` + 2px mid-edge tick.
- **Deviation edge: 1.5px dashed `#F87171` with dash-offset animation ("marching ants", 1.2s linear loop)**; static under reduced motion; always paired with a mono label `UNEXPECTED`.
- Quarantined subgraph: nodes+edges dimmed to 35% with an orange `--trust-quarantined-solid` perimeter hatch band.
- Trust propagation: edges carry a source→target gradient (state `solid` → state `solid`); a DEGRADED node spreads amber only along its outgoing edges, never recolors the target node (targets keep their own attested state).

### 6.3 Canvas treatment
- Background `--color-bg-deep` with blueprint dot grid: `radial-gradient(var(--viz-grid) 1px, transparent 1px)` at 24px pitch; optional 120px major grid lines at 4% opacity; 12% vignette at edges.
- Selected node: `--accent-glow` + `--accent-400` ring; pan/zoom chrome bottom-right; minimap bottom-left; legend top-right (required, always visible).
- No decorative particles, no starfields, no 3D perspective. The graph is evidence, not wallpaper.

---

## 7. Motion principles

Restrained, deterministic, evidence-first. Motion may never delay or obscure security state.

| Token | Value | Usage |
|---|---|---|
| `--duration-instant` | 100ms | State color/badge flips, checkbox |
| `--duration-fast` | 150ms | Hovers, tooltips, timeline tail-in |
| `--duration-base` | 200ms | Dropdowns, popovers, tabs |
| `--duration-slow` | 300ms | Modals, drawers, card lifts |
| `--duration-layout` | 450ms | Graph layout morphs, panel resize |
| `--ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Default |
| `--ease-entrance` | `cubic-bezier(0, 0, 0.2, 1)` | Enter transitions |
| `--ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Exit transitions |

Rules: no bounce/spring overshoot beyond 1.02 scale; ambient loops (rail pulse 2.4s, marching ants 1.2s) are the only infinite animations, and each is capped at one instance visible per region; skeletons 1.6s. **Reduced motion:** `@media (prefers-reduced-motion: reduce)` disables dash-offset loops, shimmer, marquee and ambient pulses; layout morphs collapse to a 1-frame crossfade; all state changes remain instant.

---

## 8. Accessibility requirements

- **Contrast:** body text ≥4.5:1, large text (≥24px or ≥18.66px bold) ≥3:1, UI components & graphical objects ≥3:1 (all tokens in §2 pre-verified; `--color-text-faint` restricted accordingly). Every trust-state pairing (§2.3) meets 4.5:1 against its tint.
- **Never color alone:** every trust state pairs color + label + glyph/shape (badges have text; graph nodes have shape+glyph; deviations add dashes + `UNEXPECTED` label).
- **Keyboard:** full tab order; graph canvas supports arrow-key node traversal (Up/Down/Left/Right = nearest-neighbor walk), Enter = open inspector, Esc = close; `Space` toggles a node's subgraph. Focus ring visible on the focused node (accent ring, 2px). Tab order never trapped except in modals (Esc releases).
- **ARIA for the graph:** container `role="group"` + `aria-label="Provenance graph, N nodes, M edges"`; each node an `role="button"` (or focusable `g`) with `aria-label="agent planner — TRUSTED, 4 outgoing edges"`; a polite live region announces traversal ("Focused: tool web-search — UNKNOWN"). Mandatory non-visual fallback: "Table view" toggle rendering the same data as a semantic `<table>` (entity, relation, state, timestamp).
- **Text alternatives:** decorative textures (`aria-hidden`), meaningful icons get labels, hashes have full value in `title`/copy affordance plus an accessible long description on certificates.
- **Motion:** per §7. **Zoom:** UI usable at 200% zoom; graph canvas has a 100%/fit control independent of browser zoom.

---

## 9. Responsive breakpoints

Tailwind v4 defaults: `sm 640` · `md 768` · `lg 1024` · `xl 1280` · `2xl 1536` (px).

- `<1024`: app sidebar collapses to icon rail (56px) or off-canvas drawer; KPI grid 4→2 columns.
- `<768`: data tables switch to stacked card rows (state badge, then mono ID, then key fields); timeline gains 16px left gutter; marketing hero clamps `--text-hero` → 40px; navigation collapses to a bottom-safe-area-aware bar.
- Graph canvas: min-height 480px on mobile with pinch-zoom; minimap hidden `<768`.
- Marketing container: `max-width: 1200px`; app shell: fluid with 24px gutters, content column `max-width: 1440px`.
- Safe areas: honor `env(safe-area-inset-*)` on fixed chrome; `overscroll-behavior` contained in scrollers.

---

## 10. Design critique checklist (apply to any screen)

1. Can a reviewer tell the trust state of the primary subject within 3 seconds, without reading color alone?
2. Is every machine-generated value (hash, ID, timestamp) in mono with tabular numerals and a copy affordance?
3. Is there exactly one interactive-accent (cyan) moment per region — no cyan competing with trust-state colors?
4. Does every state (empty, loading, error, unverified) have a designed state, with UNKNOWN used for "absence of evidence" rather than red?
5. Are all-caps strings ≤30 chars with +0.08em tracking, and never whole paragraphs?
6. Is elevation done with 1px borders first, shadow second — and at most one glow per screen?
7. Do deviation/quarantine visuals (dashed red, hatch) appear only where the data says so — zero decorative alarmism?
8. Is contrast ≥4.5:1 for all text against its actual (tinted) background, both themes?
9. Is every interactive element keyboard-reachable with a visible `:focus-visible` ring, and is the graph operable without a mouse?
10. Does the graph/table fallback pair hold — can the same data be read as a semantic table?
11. Are durations within the token set (100–450ms), with reduced-motion equivalents for every ambient loop?
12. Is spacing on the 4px grid with no ad-hoc 5px/7px/15px values?
13. Does the screen pass the "audit" voice check — factual labels, no marketing adjectives inside the product UI?
14. At 200% zoom and at 375px width, is nothing clipped, overlapped, or horizontally scrolled inside a card?
15. Would this screen still communicate with all trust colors desaturated (shape/glyph/label redundancy intact)?

---

*End of spec. All token names and values in this document are original to AegisTrace and may be pasted directly into a Tailwind CSS v4 `@theme` block (neutrals §2.1, accent §2.2, trust states §2.3, type §3.1, space/radius/shadow §4).*
