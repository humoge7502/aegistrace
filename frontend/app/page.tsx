import Link from "next/link";

const PILLARS = [
  {
    kicker: "Provenance",
    title: "Every influence, recorded",
    body: "Models, prompts, retrieval, tools, MCP servers, packages, runtime — each component attested with identity, version and digest at execution time.",
  },
  {
    kicker: "Expected vs observed",
    title: "Deviations, not vibes",
    body: "Register the expected execution contract once. At runtime, AegisTrace compares digests, component allow-lists and the causal path itself — flagging what was never supposed to happen.",
  },
  {
    kicker: "Trust propagation",
    title: "Compromise has consequences",
    body: "When a component turns bad, the causal graph answers downstream: which executions used it, which outputs depend on it, which certificates must die. Quarantine and invalidation are automatic and explainable.",
  },
  {
    kicker: "Certificates",
    title: "Verifiable trust claims",
    body: "Every trusted execution earns an AI Trust Certificate — an Ed25519-signed in-toto statement over its provenance. Verify it anywhere; revocation is immediate on compromise.",
  },
];

export default function Landing() {
  return (
    <main className="mx-auto max-w-6xl px-6">
      <nav className="flex items-center justify-between py-6" aria-label="Main">
        <div className="flex items-center gap-2.5">
          <AegisMark />
          <span className="text-lg font-bold tracking-tight">AegisTrace</span>
          <span className="microlabel mt-0.5 hidden sm:inline">runtime causal trust</span>
        </div>
        <div className="flex items-center gap-3">
          <a className="text-sm text-ink-dim transition-colors hover:text-ink" href="#thesis">Thesis</a>
          <a className="text-sm text-ink-dim transition-colors hover:text-ink" href="#pillars">Capabilities</a>
          <Link
            className="rounded-lg border border-accent/40 bg-accent/10 px-4 py-2 text-sm font-semibold text-accent transition-colors hover:bg-accent/20"
            href="/login"
          >
            Open console
          </Link>
        </div>
      </nav>

      {/* hero */}
      <section className="pb-20 pt-16 text-center sm:pt-24">
        <p className="microlabel">continuous AI execution attestation</p>
        <h1 className="mx-auto mt-4 max-w-3xl text-4xl font-bold leading-[1.1] tracking-tight sm:text-6xl">
          Prove what caused
          <br />
          <span className="text-accent">every AI output.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-ink-dim sm:text-lg">
          AegisTrace continuously builds a causal provenance graph of every component
          that influences an AI execution, verifies the observed path against its
          expected contract, propagates compromise through dependencies, and issues
          verifiable per-execution trust certificates.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            className="rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
            href="/login"
          >
            Launch the console
          </Link>
          <a
            className="rounded-lg border border-hairline px-5 py-2.5 text-sm font-medium text-ink-dim transition-colors hover:text-ink"
            href="/app/executions"
          >
            See a live trust graph →
          </a>
        </div>

        {/* mini graph signature */}
        <div className="dotgrid mx-auto mt-14 max-w-3xl rounded-xl border border-hairline p-8">
          <svg viewBox="0 0 640 170" className="w-full" role="img" aria-label="Causal execution graph: agent, retrieval, MCP server, model and output, with one deviating edge">
            <line x1="80" y1="75" x2="240" y2="30" stroke="#4ade80" strokeOpacity="0.5" />
            <line x1="80" y1="75" x2="240" y2="120" stroke="#4ade80" strokeOpacity="0.5" />
            <line x1="240" y1="120" x2="400" y2="75" stroke="#f87171" strokeOpacity="0.9" strokeDasharray="6 6" className="dev-edge" />
            <line x1="240" y1="30" x2="400" y2="75" stroke="#4ade80" strokeOpacity="0.5" />
            <line x1="400" y1="75" x2="560" y2="75" stroke="#22d3ee" strokeOpacity="0.7" />
            <circle cx="80" cy="75" r="18" fill="#22d3ee" fillOpacity="0.15" stroke="#22d3ee" />
            <rect x="222" y="12" width="36" height="36" rx="10" fill="#4ade80" fillOpacity="0.15" stroke="#4ade80" />
            <rect x="224" y="102" width="32" height="36" rx="8" fill="#4ade80" fillOpacity="0.15" stroke="#4ade80" transform="rotate(45 240 120)" />
            <rect x="378" y="53" width="44" height="44" rx="10" fill="#4ade80" fillOpacity="0.15" stroke="#4ade80" />
            <circle cx="560" cy="75" r="20" fill="#22d3ee" fillOpacity="0.15" stroke="#22d3ee" strokeDasharray="4 3" />
            <text x="80" y="118" textAnchor="middle" fill="#9aa3b5" fontSize="10" fontFamily="monospace">agent</text>
            <text x="240" y="60" textAnchor="middle" fill="#9aa3b5" fontSize="10" fontFamily="monospace">retrieval</text>
            <text x="240" y="164" textAnchor="middle" fill="#f87171" fontSize="10" fontFamily="monospace">mcp (deviated)</text>
            <text x="400" y="118" textAnchor="middle" fill="#9aa3b5" fontSize="10" fontFamily="monospace">model</text>
            <text x="560" y="118" textAnchor="middle" fill="#9aa3b5" fontSize="10" fontFamily="monospace">output</text>
          </svg>
        </div>
      </section>

      {/* thesis */}
      <section id="thesis" className="border-t border-hairline py-16">
        <p className="microlabel">the question we answer</p>
        <blockquote className="mt-4 max-w-3xl text-xl font-medium leading-relaxed sm:text-2xl">
          “Exactly which trusted components caused this particular AI action, what was
          their state at execution time, did the execution path deviate from its
          expected state — and can we cryptographically and causally prove whether the
          output should be trusted?”
        </blockquote>
        <p className="mt-6 max-w-3xl text-sm leading-relaxed text-ink-dim">
          SBOMs list components. Attestations sign builds. Observability tools show
          traces. None of them answer this question. AegisTrace joins artifact
          provenance with runtime state, execution trajectory, causal influence and
          dynamic trust propagation — and validates the difference empirically in{" "}
          <span className="mono text-accent">AttackBench</span>.
        </p>
      </section>

      {/* pillars */}
      <section id="pillars" className="border-t border-hairline py-16">
        <p className="microlabel">capabilities</p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {PILLARS.map((p) => (
            <div key={p.kicker} className="rounded-[10px] border border-hairline bg-surface p-5 transition-colors hover:border-ink-faint/40">
              <div className="microlabel text-accent">{p.kicker}</div>
              <h3 className="mt-2 text-lg font-semibold tracking-tight">{p.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-dim">{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-hairline py-8 text-xs text-ink-faint">
        <span>AegisTrace — original work. Design system: “Ledger”.</span>
        <span className="mono">predicate: aegistrace.dev/attestations/execution-trust/v1</span>
      </footer>
    </main>
  );
}

function AegisMark() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
      <path d="M13 1.5 23 5.5v7c0 6-4.4 10.4-10 12C7.4 22.9 3 18.5 3 12.5v-7L13 1.5Z" fill="#22d3ee" fillOpacity="0.12" stroke="#22d3ee" strokeWidth="1.5" />
      <path d="M8 13.2l3.4 3.4L18.5 9.5" stroke="#22d3ee" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
