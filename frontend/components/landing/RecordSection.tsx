import { Reveal, SectionHeader } from "@/components/motion";

const ENTITIES = [
  { name: "Model", meta: "kind: model", body: "Identity and digest of every model invoked — provider-served or locally served." },
  { name: "Prompt", meta: "kind: prompt", body: "System and user prompts pinned by hash. Tampering with the instruction layer is a critical deviation." },
  { name: "Retrieval", meta: "kind: corpus / document", body: "The vector index queried and every document fed into context, reduced to identifiers and SHA-256 digests." },
  { name: "Tools & MCP servers", meta: "kind: tool / mcp_server", body: "Every tool call and MCP invocation with hashed arguments and the server's attested build digest." },
  { name: "Dependencies", meta: "kind: package", body: "The package versions loaded at execution time, pinned against the expected set." },
  { name: "Runtime", meta: "kind: runtime / image", body: "The container image and interpreter the run actually executed under — not the one you hoped for." },
  { name: "Output", meta: "kind: output", body: "Every artifact an execution produces, hashed and bound to the exact causal chain that produced it." },
];

/** 01 — what gets recorded. Ledger rows, not cards. */
export function RecordSection() {
  return (
    <section id="system" aria-labelledby="record-heading" className="mx-auto max-w-6xl px-5 py-[var(--spacing-section)] sm:px-8">
      <SectionHeader
        index="01"
        kicker="provenance"
        title={<span id="record-heading">Record everything that <span className="text-accent">could have</span> influenced the answer.</span>}
        meta="events → causal graph"
      />
      <ol className="border-t border-hairline">
        {ENTITIES.map((e, i) => (
          <Reveal as="li" key={e.name} delay={i * 40}>
            <div className="ledger-row grid grid-cols-12 gap-x-4 gap-y-1 border-b border-hairline py-5">
              <span className="mono col-span-2 text-xs text-ink-faint sm:col-span-1 tnum">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="display col-span-10 text-base font-semibold tracking-tight sm:col-span-3">
                {e.name}
              </span>
              <span className="mono col-span-10 col-start-3 text-[10px] uppercase tracking-wider text-ink-faint sm:col-span-2 sm:col-start-5 sm:pt-0.5">
                {e.meta}
              </span>
              <p className="col-span-12 col-start-3 text-sm leading-relaxed text-ink-dim sm:col-span-6 sm:col-start-7">
                {e.body}
              </p>
            </div>
          </Reveal>
        ))}
      </ol>
    </section>
  );
}
