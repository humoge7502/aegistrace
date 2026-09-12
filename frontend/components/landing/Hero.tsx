import Link from "next/link";

import { Reveal } from "@/components/motion";

/** Hero graph: agent → retrieval/model → MCP (deviating) → output, with a
 * quarantined output ghost. Deliberately small SVG, pure CSS motion. */
function ProvenanceGraph() {
  return (
    <svg
      viewBox="0 0 560 300"
      className="w-full"
      role="img"
      aria-label="Causal execution graph: an agent, its retrieval and model, one deviating MCP server in red, and a quarantined output"
    >
      {/* edges */}
      <line x1="110" y1="150" x2="260" y2="60" stroke="var(--color-trust)" strokeOpacity="0.45" />
      <line x1="110" y1="150" x2="260" y2="240" stroke="var(--color-trust)" strokeOpacity="0.45" />
      <line x1="260" y1="60" x2="410" y2="150" stroke="var(--color-trust)" strokeOpacity="0.45" />
      <line x1="260" y1="240" x2="410" y2="150" stroke="var(--color-untrust)" strokeOpacity="0.9" strokeDasharray="7 6" className="dev-edge" strokeWidth="1.8" />
      <line x1="410" y1="150" x2="520" y2="150" stroke="var(--color-accent)" strokeOpacity="0.7" strokeDasharray="4 4" />

      {/* agent */}
      <circle cx="110" cy="150" r="24" fill="var(--color-accent)" fillOpacity="0.12" stroke="var(--color-accent)" />
      <text x="110" y="196" textAnchor="middle" fill="var(--color-ink-dim)" fontSize="11" fontFamily="var(--font-mono)">agent</text>

      {/* retrieval */}
      <rect x="238" y="38" width="44" height="44" rx="10" fill="var(--color-trust)" fillOpacity="0.12" stroke="var(--color-trust)" />
      <text x="260" y="26" textAnchor="middle" fill="var(--color-ink-dim)" fontSize="11" fontFamily="var(--font-mono)">retrieval</text>

      {/* mcp — deviator */}
      <rect x="244" y="218" width="32" height="44" rx="5" transform="rotate(45 260 240)" fill="var(--color-untrust)" fillOpacity="0.14" stroke="var(--color-untrust)" />
      <text x="260" y="284" textAnchor="middle" fill="var(--color-untrust)" fontSize="11" fontFamily="var(--font-mono)">mcp · deviated</text>
      <circle cx="238" cy="224" r="5" fill="var(--color-untrust)">
        <animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite" />
      </circle>

      {/* model */}
      <circle cx="410" cy="150" r="26" fill="var(--color-trust)" fillOpacity="0.12" stroke="var(--color-trust)" />
      <text x="410" y="196" textAnchor="middle" fill="var(--color-ink-dim)" fontSize="11" fontFamily="var(--font-mono)">model</text>

      {/* output */}
      <circle cx="520" cy="150" r="22" fill="var(--color-accent)" fillOpacity="0.1" stroke="var(--color-accent)" strokeDasharray="4 3" />
      <text x="520" y="196" textAnchor="middle" fill="var(--color-ink-dim)" fontSize="11" fontFamily="var(--font-mono)">output</text>
    </svg>
  );
}

export function Hero() {
  return (
    <section aria-labelledby="hero-heading" className="relative overflow-hidden">
      {/* scan rule at top */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/60 to-transparent" aria-hidden="true" />

      <div className="mx-auto grid max-w-6xl gap-12 px-5 pb-20 pt-16 sm:px-8 sm:pt-24 lg:grid-cols-12 lg:gap-8 lg:pb-28">
        {/* copy column */}
        <div className="lg:col-span-7">
          <Reveal>
            <p className="microlabel">
              runtime causal trust <span className="text-accent">·</span> ATTEST/SYS v0.1.0
            </p>
          </Reveal>
          <Reveal delay={80}>
            <h1 id="hero-heading" className="display-xl mt-6">
              Every output
              <br />
              has a <span className="text-accent">past.</span>
            </h1>
          </Reveal>
          <Reveal delay={160}>
            <p className="mt-7 max-w-xl text-lg leading-relaxed text-ink-dim">
              AegisTrace records the causal provenance of every component behind an
              AI execution — model, prompt, retrieval, tools, MCP servers, runtime —
              verifies the observed run against its expected contract, and quarantines
              everything a compromise touched.
            </p>
          </Reveal>
          <Reveal delay={240}>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link
                href="/login"
                className="rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
              >
                Open the console
              </Link>
              <a
                href="#thesis"
                className="navlink rounded-lg px-2 py-3 text-sm font-medium text-ink-dim transition-colors hover:text-ink"
              >
                Read the thesis
              </a>
            </div>
          </Reveal>
          <Reveal delay={320}>
            <dl className="mono mt-12 grid max-w-xl grid-cols-2 gap-x-8 gap-y-2 text-[11px] text-ink-faint sm:grid-cols-3">
              <div className="min-w-0">
                <dt className="sr-only">Predicate</dt>
                <dd className="truncate">predicate: aegistrace.dev/attestations/execution-trust/v1</dd>
              </div>
              <div className="min-w-0">
                <dt className="sr-only">Signature</dt>
                <dd className="truncate">signature: ed25519 · canonical json</dd>
              </div>
              <div>
                <dt className="sr-only">Principle</dt>
                <dd>unknown ≠ trusted</dd>
              </div>
            </dl>
          </Reveal>
        </div>

        {/* graph column */}
        <Reveal delay={200} className="lg:col-span-5">
          <div className="dotgrid rounded-xl border border-hairline bg-surface p-5 lg:mt-8">
            <div className="mb-2 flex items-center justify-between">
              <span className="microlabel">execution · demo-run-1</span>
              <span className="mono text-[10px] text-untrust">UNTRUSTED</span>
            </div>
            <ProvenanceGraph />
            <p className="mono mt-2 border-t border-hairline pt-3 text-[10px] leading-relaxed text-ink-faint">
              observed path deviated at step 3 — output quarantined, certificate revoked
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
