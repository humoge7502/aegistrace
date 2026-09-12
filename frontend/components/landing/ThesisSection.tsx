import { Reveal, SectionHeader } from "@/components/motion";

/** 00 — the question the product exists to answer. */
export function ThesisSection() {
  return (
    <section id="thesis" aria-labelledby="thesis-heading" className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] sm:px-8">
      <SectionHeader index="00" kicker="the question" meta="why this exists" />
      <Reveal>
        <blockquote id="thesis-heading" className="max-w-4xl">
          <p className="display-lg text-balance">
            “Exactly which components caused <em className="text-accent not-italic">this</em> output,
            did the path deviate — and can you <em className="text-accent not-italic">prove</em> it?”
          </p>
        </blockquote>
      </Reveal>
      <Reveal delay={120}>
        <div className="mt-10 grid gap-8 lg:grid-cols-12">
          <div className="lg:col-span-5 lg:col-start-8">
            <p className="text-base leading-relaxed text-ink-dim">
              SBOMs list components. Build attestations sign artifacts. Observability
              shows traces. None of them answer the question — because the question is
              about <strong className="font-semibold text-ink">runtime causality</strong>:
              what influenced a specific execution, in what state, along which path.
            </p>
            <p className="mt-4 text-base leading-relaxed text-ink-dim">
              AegisTrace is built to answer it — with evidence, not scores.
            </p>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
