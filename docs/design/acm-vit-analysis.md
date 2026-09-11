# ACM-VIT Website — Design Research Notes (for AegisTrace)

- **Source analyzed:** https://www.acmvit.in/
- **Date of analysis:** 2026-09-12
- **Method:** WebFetch (rendered-content summary) + raw HTML download (557,004 bytes) + compiled stylesheet download (`/_astro/index.B4qmX8U6.css`, 118,690 bytes).
- **Purpose:** Extract transferable *design principles* only. AegisTrace deliberately does **not** reuse ACM-VIT's logo, name, text, palette, imagery, or any asset. Every observation below is labeled:
  - **OBSERVED** — directly evidenced in the fetched HTML/CSS/markdown (evidence quoted).
  - **GENERAL-PRINCIPLE** — a genre-level best practice for well-regarded tech-community/developer sites, stated because it informs AegisTrace; not a claim about acmvit.in.

---

## 1. What could and could not be verified

### Could verify (OBSERVED)
- The site was fully reachable and server-rendered: 557 KB of complete HTML with real content in the document (no JS required to read headings, nav, cards, footer).
- Stack: an Astro build — `data-astro-cid-*` scoped-style attributes throughout, assets under `/_astro/`, stylesheet `/_astro/index.B4qmX8U6.css`. No `__NEXT_DATA__`; the compiled CSS contains Tailwind-style utility classes with the Tailwind v4 `--tw-*` custom-property architecture (e.g., `--tw-backdrop-blur`, `--default-transition-duration`).
- Fonts: Google Fonts `Inter:wght@400;700;900` is loaded via `<link>`; body font stack is `font-family:PolySans Trial,Inter,Roboto,Helvetica Neue,Arial Nova,Nimbus Sans,Arial,sans-serif` (OBSERVED in the `body{}` rule). "PolySans" (Bold / Bulky Wide / Slim variants appear in inline styles) is a commercial display family; "Trial" in the name suggests an unlicensed/trial weight fallback chain.
- Colors (hex literals present in the HTML/CSS): near-black backgrounds `#0d0e0d`, `#060606`, `#050505`; dominant text/cream `#FFFDD0` / `#FEFCD9`; primary accent coral `#F95F4A` / `#FF5F4A`; per-item accent via CSS variable (`background:var(--proj-color, #f95f4a)`); secondary accents pink `#FF007A`, purple `#8710DB` / `#7100FF`, blue `#2664E4`, green `#16A34A`, orange `#FF6B35`, red `#EB5757`; grays `#999999`, `#CCCCCC`; translucent accent tints like `background-color:#f95f4a1a`.
- Motion: `@keyframes` for `fadeIn, fadeInUp, float, marquee, partners-marquee, pulse, rotate, shimmer, slideInUp, spin, footer-starfield-breathe`; `prefers-reduced-motion: reduce` blocks (5 occurrences) and one `prefers-reduced-data: reduce`; transition durations 200–700 ms with easing `cubic-bezier(.25,.1,.25,1)`; `@media (hover:hover)` guards.
- Layout & interaction utilities: `max-w-[1400px]` containers; grids of 1/2/3/10 columns; gaps 8–24 px (`gap-2`…`gap-6`); `rounded-lg` is the dominant radius (445 occurrences) plus pills (`rounded-full`, `rounded-[41px]`); hover effects `hover:scale-105/110`, `hover:translate-y-0` (cards rest lifted), `hover:shadow-2xl`; floating fixed header `class="site-header fixed top-5 left-0 right-0 z-50 ..."` with `backdrop-blur-sm`; scroll-state class `body.hero-in-view .site-header { top:auto; bottom: ... }` relocates the header to the viewport bottom while the hero is in view; pinned sections `sticky top-0 h-screen`; background textures `diamond-grid`, `repeating-linear-gradient(...var(--dot-fill) 0 3px, transparent...)`, canvas elements (4).
- Semantics: 1 `header`, 1 `nav`, 1 `main`, 37 `section`, 14 `article`, 2 `footer`, 21 `button`, 2 `form`, ~700 `img`; 60 `aria-*` attributes; `role="dialog"`, `role="button"`; mostly descriptive `alt` text ("ACM-VIT Logo" ×56, "Board Moment", "Event Highlight"…) with some intentional `alt=""`.
- Responsive: Tailwind `sm/md/lg` breakpoints in class strings (e.g., `text-5xl sm:text-6xl md:text-7xl lg:text-[8rem]`); media queries at 768 px (×9), 576 px, 480 px, min-width 40/48/64/80/96 rem, plus bespoke widths (952/987/1320 px); a mobile menu button state class `body.mobile-menu-open`.
- Accessibility weaknesses also OBSERVED: 6 `h1` elements on one page; `focus:outline-none` present; only 2 `tabindex="0"` and 20 `aria-hidden="true"`; focus-visible ring utilities exist but appear sparse (`focus-visible:ring-primary-pink` once).

### Could not verify (honest gaps)
- Rendered/runtime visuals: no headless-browser screenshot was taken, so final computed colors, font rendering (especially the licensed "PolySans" display face vs. its fallbacks), and real interaction behavior are unverified.
- JS behavior: marquee/scroll effects are strongly implied by keyframes and state classes but the actual runtime feel was not executed.
- Lighthouse/a11y audit scores, keyboard operability, screen-reader output.
- Exact visual section order as a user perceives it (the WebFetch text order may differ from DOM order).
- Whether contrast ratios of the cream-on-black text meet WCAG AA at runtime (not computed against rendered pixels).

---

## 2. Information architecture (OBSERVED)

Single-page scroll site with anchor navigation (ABOUT, DOMAINS, EVENTS, PROJECTS, ACM-W, MORE) plus a few real routes (e.g., `/grep`, `/team`-style pages). Long-form content is organized into catalog-like collections: events grid (~11 items with index IDs such as `#4kmu-0000/11`), project cards (~7, each with "VISIT WEBSITE" links), team cards (~16 with LinkedIn/GitHub), blog list (~17 posts), a photo gallery, and a contact form. Footer carries six link columns and a status line ("All systems online" — OBSERVED text).

**Takeaway (principle):** a clear nav taxonomy of 5–6 top-level items + a "more" overflow, collection grids with stable identity (index IDs), and a rich footer work as a genre pattern. AegisTrace will use 5 primary app destinations (Overview, Provenance Graph, Attestations/Certificates, Incidents, Policy) — our own structure, not theirs.

## 3. Hero composition (OBSERVED pattern)

Award/banner strip → very large uppercase typographic hero (`text-5xl … lg:text-[8rem]`, `leading-[0.85]`, `tracking-tighter`, cream on near-black) → one bracketed terminal-style CTA → animated word marquee. The hero is a full-viewport pinned/sticky composition.

**GENERAL-PRINCIPLE takeaways for AegisTrace:** one dominant typographic or data moment in the hero; a single primary CTA; tight leading on display type; motion should be ambient (marquee/pulse) rather than attention-hijacking. AegisTrace's hero equivalent: a live mini provenance-graph or an attestation "certificate of the moment" instead of decorative art.

## 4. Typography scale and rules (OBSERVED)

- Display: huge uppercase headings, `font-bold`, `leading-[0.85–0.9]`, `tracking-tighter`, responsive in 4 steps (mobile-first).
- Micro-labels/kickers: `uppercase tracking-wider` at `text-base`, coral accent color — used on card headers (OBSERVED `<h3 class="... uppercase tracking-wider mb-2 text-base">`).
- Letter-spaced section labels ("E V E N T S" spaced text appears in content).
- Font pairing: commercial display family + free workhorse (Inter 400/700/900) — a display/UI split.

**GENERAL-PRINCIPLE takeaways:** keep a strict 2-family system (display/UI + mono for technical strings), a 4-step responsive display scale, ALL-CAPS only for short micro-labels with generous tracking, and a dedicated mono voice for hashes/IDs. AegisTrace adopts this structure with its own original faces (IBM Plex Sans + JetBrains Mono) and its own scale (see design system).

## 5. Color usage (OBSERVED)

Near-black base (`#0d0e0d`) with a warm off-white text (`#FFFDD0`-cream) and **one loud accent** (coral `#F95F4A`) carrying CTAs, kickers, and hover states; a set of secondary hues is used as *per-item identity* colors via CSS custom properties (`--proj-color`). Accent-tinted translucent fills (`#f95f4a1a`) mark interactive/hover surfaces.

**GENERAL-PRINCIPLE takeaways:** dark-first base + near-white warm text + a single accent hue that owns "interactive"; secondary hues should encode *data identity* (per-entity), not decoration; use low-alpha tints of a hue rather than new hues for hover/selected states. AegisTrace generalizes this into a semantic trust-state palette (8 states) with cyan as the single interactive accent.

## 6. Spacing, cards, sections (OBSERVED)

Base padding `px-4` (16 px) with small gaps (8–24 px) — a compact, dense rhythm; cards use 1px-ish borders, `rounded-lg`, image/icon + kicker + title + link structure, lift-on-hover (`hover:translate-y-0` implies resting `translate-y` offset, `hover:shadow-2xl`); sections are full-bleed with pinned scroll storytelling; container `max-w-[1400px]`.

**GENERAL-PRINCIPLE takeaways:** pick one container width and one card recipe and repeat them relentlessly; hover = small lift + shadow + tint, nothing more. AegisTrace uses an 8-pt-ish 4 px grid, 1,280 px content max-width (denser, enterprise), and cards that state trust state up front.

## 7. Motion and interaction (OBSERVED)

Marquee tickers (hero + partners), float/pulse ambient loops, shimmer for loading, entrance `fadeIn/fadeInUp/slideInUp`, spin/rotate accents, starfield breathing in the footer; `duration-300` is the dominant transition (256 uses); durations 200–700 ms; easing `cubic-bezier(.25,.1,.25,1)`; `@media (hover:hover)` guards hover effects; `prefers-reduced-motion` is honored (5 blocks).

**GENERAL-PRINCIPLE takeaways:** ambient motion should be continuous and slow; feedback motion should be 150–300 ms; always gate on `prefers-reduced-motion` and `(hover:hover)`. AegisTrace adds a stricter rule: motion may *never* delay access to security-critical state.

## 8. Responsive behavior (OBSERVED signals)

Mobile-first Tailwind breakpoints; dedicated mobile menu state; several bespoke breakpoints (952/987/1320 px) tuned per-section; `env(safe-area-inset-bottom)` used in header positioning (notch-aware); `overscroll-behavior-y:none` on body.

**GENERAL-PRINCIPLE takeaways:** mobile-first with per-component overrides where default scales break; honor device safe areas; guard against horizontal scroll (`overflow-x` discipline). AegisTrace: sidebar collapses <1024 px, tables become cards <768 px, graph canvas keeps a 480 px minimum height.

## 9. Accessibility signals (OBSERVED)

Good: semantic landmarks (`header/nav/main/section/article/footer`), descriptive `alt` text on most of ~700 images, 60 `aria-*` attributes, `role="dialog"`, reduced-motion support, `@media (hover:hover)` guards.
Weak (also OBSERVED): six `h1` elements (heading hierarchy noise), sparse focus-visible styling, minimal `tabindex` management.

**GENERAL-PRINCIPLE takeaways:** one `h1` per page; a visible, consistent focus ring on every interactive element; decorative media gets `alt=""`/`aria-hidden`; for AegisTrace the graph is the extra obligation — it needs a keyboard traversal model, per-node labels, and a non-visual table fallback.

## 10. Distinctive ideas worth borrowing as *principles* (not assets)

1. **Catalog identity (OBSERVED index IDs like `#4kmu-0000/11`):** giving every item a stable, monospace, machine-feeling identifier creates an "evidence ledger" aesthetic. AegisTrace turns this into per-execution attestation IDs and certificate serials — original implementation.
2. **Status-as-interface (OBSERVED "All systems online" footer):** surfacing live system state as a permanent UI element builds trust. AegisTrace generalizes: a persistent trust-state rail on every screen.
3. **Terminal-honest CTAs (OBSERVED bracketed `[ ... ]` CTA):** technical voice signals authenticity. AegisTrace uses mono-voiced micro-labels and verbatim hashes rather than decorative brackets, to avoid imitating the site.
4. **Texture over decoration (OBSERVED `diamond-grid`, dotted `repeating-linear-gradient`, canvas starfield):** subtle geometric texture gives depth without gradient-glow clichés. AegisTrace uses a blueprint dot-grid on graph canvases only.
5. **Scroll-state chrome (OBSERVED header relocating via `body.hero-in-view`):** chrome that responds to scroll position keeps the viewport clean. AegisTrace keeps a conventional sticky header — this product's density argues against moving chrome.

## 11. What AegisTrace deliberately does differently

- **OBSERVED genre risk (GENERAL-PRINCIPLE):** playful community sites lean on loud coral/cream, marquees, and humor; an enterprise attestation product must read as calm, forensic, and audit-grade. AegisTrace uses a restrained slate-black/cyan system where color primarily *encodes trust state*, not brand energy.
- No copying: no cream/coral palette, no PolySans, no marquee-heavy motion language, no cassette/retro motif, no ACM-VIT text, logos, or imagery. All AegisTrace tokens in the companion design system are original selections chosen for WCAG-AA contrast on both themes.

---

**Companion document:** `aegistrace-design-system.md` (original AegisTrace visual identity and token spec).

*This analysis is a research artifact; all OBSERVED claims are evidence-backed by the fetches listed in §1, and nothing in it should be read as permission to reuse ACM-VIT's protected branding.*
