import Link from "next/link";

import { AegisMark } from "@/components/landing/SiteHeader";
import { Reveal } from "@/components/motion";

export function ClosingCTA() {
  return (
    <section aria-labelledby="cta-heading" className="rule-t">
      <div className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] text-center sm:px-8">
        <Reveal>
          <p className="microlabel">next step</p>
          <h2 id="cta-heading" className="display-lg mx-auto mt-6 max-w-3xl text-balance">
            Ask your agent&apos;s outputs <span className="text-accent">who they are.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-ink-dim">
            Instrument one agent with the SDK, register its baseline, and watch the
            first compromised run name exactly what changed.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/login"
              className="rounded-lg bg-accent px-6 py-3 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
            >
              Open the console
            </Link>
            <Link
              href="/app/executions"
              className="rounded-lg border border-hairline-strong px-6 py-3 text-sm font-medium text-ink-dim transition-colors hover:border-ink-faint hover:text-ink"
            >
              Browse executions
            </Link>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

export function SiteFooter() {
  const cols = [
    {
      title: "product",
      links: [
        { label: "Console", href: "/app" },
        { label: "Executions", href: "/app/executions" },
        { label: "Certificates", href: "/app/certificates" },
        { label: "AttackBench", href: "/app/attackbench" },
      ],
    },
    {
      title: "documentation",
      links: [
        { label: "Architecture", href: "/docs/architecture/architecture.md" },
        { label: "Trust model", href: "/docs/architecture/trust-model.md" },
        { label: "API reference", href: "/docs/architecture/api.md" },
        { label: "SDK guide", href: "/docs/architecture/sdk.md" },
      ],
    },
    {
      title: "proof",
      links: [
        { label: "AttackBench results", href: "/docs/benchmarks/attackbench-results.json" },
        { label: "Comparison", href: "/docs/benchmarks/comparison.md" },
        { label: "Threat model", href: "/docs/security/threat-model.md" },
        { label: "Final report", href: "/docs/FINAL-REPORT.md" },
      ],
    },
  ];
  return (
    <footer className="rule-t bg-canvas-2">
      <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8">
        <div className="grid gap-10 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <div className="flex items-center gap-2.5">
              <AegisMark />
              <span className="display text-lg tracking-tight">AegisTrace</span>
            </div>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-ink-dim">
              Continuous AI execution attestation and runtime causal trust.
              Simple to understand. Difficult to forget.
            </p>
            <p className="mono mt-6 text-[10px] text-ink-faint">
              predicate aegistrace.dev/attestations/execution-trust/v1 · ed25519
            </p>
          </div>
          {cols.map((col) => (
            <nav key={col.title} aria-label={col.title} className="lg:col-span-2">
              <p className="microlabel">{col.title}</p>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a href={l.href} className="text-sm text-ink-dim transition-colors hover:text-ink">
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
          <div className="lg:col-span-1" />
        </div>
        <div className="mono mt-12 flex flex-wrap items-center justify-between gap-3 border-t border-hairline pt-6 text-[10px] text-ink-faint">
          <span>© 2026 AegisTrace — original work, “Ledger” design system</span>
          <span>status: demo build · v0.1.0</span>
        </div>
      </div>
    </footer>
  );
}
