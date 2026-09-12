import { TRUST_COLORS, type TrustState } from "@/lib/trust";

const STATES: { state: TrustState; note: string }[] = [
  { state: "TRUSTED", note: "all checks passed" },
  { state: "DEGRADED", note: "minor deviation" },
  { state: "UNKNOWN", note: "insufficient evidence" },
  { state: "UNTRUSTED", note: "critical deviation" },
  { state: "COMPROMISED", note: "attacker-controlled" },
  { state: "QUARANTINED", note: "isolated from use" },
  { state: "RECOVERING", note: "restore in progress" },
  { state: "RE-CERTIFIED", note: "re-verified after recovery" },
];

/** Full-bleed ticker of the eight trust states — the domain, at a glance. */
export function TrustTicker() {
  const row = [...STATES, ...STATES];
  return (
    <section aria-label="The eight trust states" className="rule-t rule-b overflow-hidden bg-canvas-2">
      <div className="ticker-track flex w-max items-center gap-10 py-3.5">
        {row.map((s, i) => {
          const c = TRUST_COLORS[s.state];
          return (
            <span key={i} className="flex items-center gap-2.5 whitespace-nowrap">
              <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: c.hex }} aria-hidden="true" />
              <span className="mono text-xs font-medium" style={{ color: c.hex }}>
                {s.state}
              </span>
              <span className="mono text-[10px] text-ink-faint">{s.note}</span>
              <span className="ml-6 text-ink-faint/50" aria-hidden="true">/</span>
            </span>
          );
        })}
      </div>
    </section>
  );
}
