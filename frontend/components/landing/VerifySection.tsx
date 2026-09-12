import { Reveal, SectionHeader } from "@/components/motion";

const BASELINE_SAMPLE = `{
  "agent_ref": "support-agent",
  "mode": "sequence",
  "steps": [
    { "seq": 1, "kind": "model",     "target": "demo-model@1" },
    { "seq": 2, "kind": "retrieval", "target": "kb://policies" },
    { "seq": 3, "kind": "mcp",       "target": "mcp://crm" }
  ],
  "component_digests": { "mcp://crm": "sha256:bb…" },
  "prompt_hashes":     { "system":   "sha256:aa…" }
}`;

const DEVIATIONS = [
  { kind: "digest_mismatch", sev: "critical", body: "A component's build differs from its pinned digest." },
  { kind: "unexpected_component", sev: "critical", body: "A tool, server or source outside the allow-list entered the path." },
  { kind: "prompt_mismatch", sev: "critical", body: "The instruction layer changed under you." },
  { kind: "path_deviation", sev: "high", body: "The execution wandered off its expected sequence." },
  { kind: "missing_step", sev: "medium", body: "An expected step never happened — evidence withheld." },
];

/** 02 — expected vs observed. Asymmetric split: code + deviation table. */
export function VerifySection() {
  return (
    <section aria-labelledby="verify-heading" className="rule-t bg-canvas-2">
      <div className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] sm:px-8">
        <SectionHeader
          index="02"
          kicker="expected vs observed"
          title={<span id="verify-heading">Write the contract once. <span className="text-accent">Every run</span> is checked against it.</span>}
          meta="baselines · deviation detection"
        />
        <div className="grid gap-10 lg:grid-cols-12">
          <Reveal className="min-w-0 lg:col-span-5">
            <p className="text-base leading-relaxed text-ink-dim">
              A <strong className="font-semibold text-ink">baseline</strong> is the
              execution contract: the expected sequence, the allowed component sets,
              the pinned digests, the prompt hashes. The SDK attests what actually
              happened; the engine diffs the two and classifies every difference.
            </p>
            <p className="mt-4 text-base leading-relaxed text-ink-dim">
              Probabilistic pipelines are supported — <span className="mono text-sm">allowed_set</span> mode
              permits any order, and <span className="mono text-sm">policy_only</span> mode checks
              digests alone.
            </p>
            <div className="mono mt-8 overflow-hidden rounded-lg border border-hairline bg-canvas">
              <div className="rule-b flex items-center justify-between px-4 py-2">
                <span className="microlabel">baseline.json</span>
                <span className="mono text-[10px] text-ink-faint">expected contract</span>
              </div>
              <pre className="overflow-x-auto p-4 text-[11px] leading-relaxed text-ink-dim">{BASELINE_SAMPLE}</pre>
            </div>
          </Reveal>

          <div className="lg:col-span-6 lg:col-start-7">
            <Reveal>
              <p className="microlabel mb-4">deviation taxonomy</p>
            </Reveal>
            <ul className="border-t border-hairline">
              {DEVIATIONS.map((d, i) => (
                <Reveal as="li" key={d.kind} delay={i * 60}>
                  <div className="ledger-row grid grid-cols-12 gap-2 border-b border-hairline py-4">
                    <span
                      className="mono col-span-12 self-start px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider sm:col-span-3"
                      style={{
                        color: d.sev === "critical" ? "var(--color-untrust)" : d.sev === "high" ? "var(--color-quarantined)" : "var(--color-degraded)",
                      }}
                    >
                      {d.sev}
                    </span>
                    <span className="mono col-span-12 text-xs font-medium sm:col-span-4">{d.kind}</span>
                    <span className="col-span-12 text-sm leading-relaxed text-ink-dim sm:col-span-5">{d.body}</span>
                  </div>
                </Reveal>
              ))}
            </ul>
            <Reveal delay={200}>
              <p className="mt-6 text-sm leading-relaxed text-ink-faint">
                Severity maps to trust state through an explicit, auditable policy —
                never an opaque score. Any critical deviation: <span className="mono text-xs text-untrust">UNTRUSTED</span>.
              </p>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}
