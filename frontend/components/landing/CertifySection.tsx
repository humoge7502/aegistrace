import { Reveal, SectionHeader } from "@/components/motion";

/** Certificate art — notched corner, mono serial, verified stamp. */
function CertificateArt() {
  return (
    <div className="relative overflow-hidden rounded-lg border-2 border-hairline-strong bg-surface p-6">
      <div
        className="absolute right-0 top-0 h-7 w-7 bg-canvas"
        style={{ clipPath: "polygon(100% 0, 100% 100%, 0 0)" }}
        aria-hidden="true"
      />
      <div className="flex items-start justify-between">
        <div>
          <p className="microlabel">ai trust certificate</p>
          <p className="mono mt-2 text-lg font-semibold text-accent">ATC-69776485103ae647</p>
        </div>
        <span className="stamp mono inline-block rounded border-2 border-trust px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-trust">
          verified
        </span>
      </div>
      <dl className="mono mt-5 space-y-1.5 text-[11px] text-ink-dim">
        <div className="flex justify-between gap-6"><dt className="text-ink-faint">subject</dt><dd className="truncate">execution:demo-run-1</dd></div>
        <div className="flex justify-between gap-6"><dt className="text-ink-faint">digest</dt><dd>sha256:7f3c…9a10</dd></div>
        <div className="flex justify-between gap-6"><dt className="text-ink-faint">predicate</dt><dd className="truncate">…/attestations/execution-trust/v1</dd></div>
        <div className="flex justify-between gap-6"><dt className="text-ink-faint">signature</dt><dd>ed25519:Wf8nT…</dd></div>
        <div className="flex justify-between gap-6"><dt className="text-ink-faint">status</dt><dd className="text-trust">ACTIVE</dd></div>
      </dl>
      <p className="mono mt-5 border-t border-hairline pt-3 text-[10px] leading-relaxed text-ink-faint">
        in-toto Statement v1 · verifiable anywhere · revocation is immediate on compromise
      </p>
    </div>
  );
}

/** 04 — certification. */
export function CertifySection() {
  return (
    <section aria-labelledby="certify-heading" className="rule-t bg-canvas-2">
      <div className="mx-auto grid max-w-6xl gap-10 px-5 py-[var(--spacing-section)] sm:px-8 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <SectionHeader
            index="04"
            kicker="certification"
            title={<span id="certify-heading">Trust you can <span className="text-accent">check</span>, not trust you must assume.</span>}
            meta="ed25519 · in-toto"
          />
          <Reveal>
            <p className="text-base leading-relaxed text-ink-dim">
              Every execution that passes all checks earns a certificate: an Ed25519
              signature over a canonical in-toto statement of its provenance. Verify
              it in the console, from CI, or from your own tooling — the signature is
              the proof, the revocation list is the truth.
            </p>
          </Reveal>
          <Reveal delay={120}>
            <ul className="mono mt-8 space-y-2 text-xs text-ink-dim">
              <li className="rule-t pt-2">POST /api/v1/certificates/&#123;serial&#125;/verify</li>
              <li className="rule-t pt-2">signature + revocation + subject-fingerprint match</li>
              <li className="rule-t pt-2">forged statements are rejected — AttackBench case 12</li>
            </ul>
          </Reveal>
        </div>
        <Reveal delay={160} className="lg:col-span-6 lg:col-start-7">
          <CertificateArt />
        </Reveal>
      </div>
    </section>
  );
}
