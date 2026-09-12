import Link from "next/link";

import { Reveal, SectionHeader } from "@/components/motion";

const STATS = [
  { value: "14/14", label: "attack scenarios detected", note: "AttackBench v0 fixtures" },
  { value: "0", label: "false positives on benign controls", note: "3 controls, incl. recovery flow" },
  { value: "36% → 100%", label: "SBOM-only vs full pipeline recall", note: "same fixtures, same evidence" },
  { value: "100%", label: "forged certificates rejected", note: "signature + subject + revocation" },
];

/** Evidence band — real, reproducible numbers (docs/benchmarks/). */
export function EvidenceSection() {
  return (
    <section id="evidence" aria-labelledby="evidence-heading" className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] sm:px-8">
      <SectionHeader
        index="05"
        kicker="evidence"
        title={<span id="evidence-heading">The differentiation is <span className="text-accent">measured</span>, not claimed.</span>}
        meta="reproducible: benchmarks/"
      />
      <dl className="grid gap-px overflow-hidden rounded-xl border border-hairline bg-hairline sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((s, i) => (
          <Reveal key={s.label} delay={i * 70}>
            <div className="flex h-full flex-col bg-surface p-6">
              <dd className="display text-4xl tracking-tight text-accent tnum">{s.value}</dd>
              <dt className="mt-3 text-sm font-medium leading-snug">{s.label}</dt>
              <p className="mono mt-auto pt-4 text-[10px] text-ink-faint">{s.note}</p>
            </div>
          </Reveal>
        ))}
      </dl>
      <Reveal delay={200}>
        <p className="mt-5 text-sm leading-relaxed text-ink-faint">
          All numbers regenerate from the repository —{" "}
          <span className="mono text-xs">python benchmarks/attackbench/run_attackbench.py</span>. See{" "}
          <Link href="/app/attackbench" className="navlink text-accent">the AttackBench console</Link>{" "}
          for the per-scenario matrix.
        </p>
      </Reveal>
    </section>
  );
}
