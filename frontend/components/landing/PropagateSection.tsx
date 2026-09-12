import { Reveal, SectionHeader } from "@/components/motion";

/** Compromise chain: component → execution → output → certificate, with the
 * invalidation flowing downstream. Pure SVG + CSS motion. */
function ChainDiagram() {
  const node = (x: number, y: number, label: string, sub: string, color: string, dashed = false) => (
    <g>
      <rect x={x} y={y} width={148} height={54} rx={10}
        fill={color} fillOpacity="0.08" stroke={color}
        strokeDasharray={dashed ? "5 4" : undefined} strokeWidth={1.4} />
      <text x={x + 74} y={y + 23} textAnchor="middle" fill="var(--color-ink)" fontSize="12" fontWeight="600" fontFamily="var(--font-display)">{label}</text>
      <text x={x + 74} y={y + 40} textAnchor="middle" fill={color} fontSize="9.5" fontFamily="var(--font-mono)">{sub}</text>
    </g>
  );
  const arrow = (x1: number, y: number, x2: number, color: string, animated = false) => (
    <g>
      <line x1={x1} y1={y} x2={x2} y2={y} stroke={color} strokeWidth={1.4}
        strokeDasharray={animated ? "6 5" : undefined}
        className={animated ? "dev-edge" : undefined} strokeOpacity={animated ? 0.95 : 0.5} />
      <path d={`M ${x2} ${y - 4} L ${x2 + 7} ${y} L ${x2} ${y + 4} Z`} fill={color} stroke="none" />
    </g>
  );
  return (
    <svg viewBox="0 0 700 330" className="w-full" role="img"
      aria-label="Compromise propagation: a compromised MCP server invalidates the execution that used it, quarantines its output, and revokes its certificate">
      {node(20, 30, "MCP server", "COMPROMISED", "var(--color-compromised)")}
      {arrow(172, 57, 216, "var(--color-compromised)", true)}
      {node(220, 30, "Execution #8472", "UNTRUSTED", "var(--color-untrust)")}
      {arrow(372, 57, 416, "var(--color-untrust)", true)}
      {node(420, 30, "Output #238", "QUARANTINED", "var(--color-quarantined)")}

      <path d="M 494 84 C 494 130, 294 130, 294 168" fill="none" stroke="var(--color-quarantined)" strokeOpacity="0.6" strokeWidth={1.2} strokeDasharray="4 4" />
      {node(220, 170, "Certificate", "REVOKED", "var(--color-untrust)", true)}
      {arrow(372, 197, 416, "var(--color-ink-faint)")}
      {node(420, 170, "Incident", "OPEN · evidence", "var(--color-recovering)")}

      <text x="20" y="286" fill="var(--color-ink-dim)" fontSize="12.5" fontFamily="var(--font-sans)">
        Every hop is recorded as evidence — the chain is the explanation.
      </text>
      <text x="20" y="308" fill="var(--color-ink-faint)" fontSize="11" fontFamily="var(--font-mono)">
        GET /api/v1/components/{""}{""}mcp:crm{""}/impact → executions, outputs, certificates
      </text>
    </svg>
  );
}

/** 03 — propagation. */
export function PropagateSection() {
  return (
    <section aria-labelledby="propagate-heading" className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] sm:px-8">
      <SectionHeader
        index="03"
        kicker="trust propagation"
        title={<span id="propagate-heading">Compromise flows <span className="text-accent">downstream</span>. So does the proof.</span>}
        meta="causal invalidation"
      />
      <div className="grid gap-10 lg:grid-cols-12">
        <Reveal className="lg:col-span-7">
          <div className="dotgrid rounded-xl border border-hairline bg-surface p-6">
            <ChainDiagram />
          </div>
        </Reveal>
        <Reveal delay={120} className="lg:col-span-5">
          <p className="text-base leading-relaxed text-ink-dim">
            When a component is marked compromised — by digest evidence or by an
            operator — the engine walks the causal graph and answers the hard
            question: <strong className="font-semibold text-ink">what else was affected?</strong>
          </p>
          <ul className="mt-6 space-y-3 text-sm leading-relaxed text-ink-dim">
            <li className="rule-t pt-3">Executions that used it are invalidated — historically, not just going forward.</li>
            <li className="rule-t pt-3">Dependent outputs are quarantined before anyone consumes them.</li>
            <li className="rule-t pt-3">Their certificates are revoked, with the reason preserved.</li>
            <li className="rule-t pt-3">One incident holds the full affected list and the evidence chains.</li>
          </ul>
          <p className="mt-6 text-sm leading-relaxed text-ink-faint">
            Recovery never silently re-trusts history. Only a verified re-run earns
            <span className="mono text-xs text-recertified"> RE-CERTIFIED</span>.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
