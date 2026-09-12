import { TRUST_COLORS, type TrustState } from "@/lib/trust";

export function TrustBadge({ state, small }: { state: string; small?: boolean }) {
  const c = TRUST_COLORS[state as TrustState] ?? TRUST_COLORS.UNKNOWN;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${c.border} ${c.bg} ${c.text} ${
        small ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs"
      } font-semibold tracking-wide`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${c.text}`} style={{ backgroundColor: "currentColor" }} />
      {state}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const color =
    severity === "critical" ? "text-untrust border-untrust/40"
    : severity === "high" ? "text-quarantined border-quarantined/40"
    : severity === "medium" ? "text-degraded border-degraded/40"
    : "text-unknown border-unknown/40";
  return (
    <span className={`inline-flex rounded border ${color} px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider`}>
      {severity}
    </span>
  );
}

export function Card({ title, action, children, className }: {
  title?: string; action?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <section className={`min-w-0 rounded-[10px] border border-hairline bg-surface ${className ?? ""}`}>
      {title ? (
        <header className="flex items-center justify-between border-b border-hairline px-4 py-2.5">
          <h2 className="microlabel">{title}</h2>
          {action}
        </header>
      ) : null}
      <div className="p-4">{children}</div>
    </section>
  );
}

export function StatTile({ label, value, state, hint }: {
  label: string; value: number | string; state?: string; hint?: string;
}) {
  const color = state ? `text-[var(--color-${stateToCss(state)})]` : "text-ink";
  return (
    <div className="min-w-0 rounded-[10px] border border-hairline bg-surface px-4 py-3">
      <div className="microlabel">{label}</div>
      <div className={`mono mt-1 text-2xl font-semibold tnum ${color}`}>{value}</div>
      {hint ? <div className="mt-0.5 text-xs text-ink-faint">{hint}</div> : null}
    </div>
  );
}

function stateToCss(state: string): string {
  const map: Record<string, string> = {
    TRUSTED: "trust", UNTRUSTED: "untrust", UNKNOWN: "unknown", DEGRADED: "degraded",
    COMPROMISED: "compromised", QUARANTINED: "quarantined", RECOVERING: "recovering",
    "RE-CERTIFIED": "recertified",
  };
  return map[state] ?? "unknown";
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[10px] border border-dashed border-hairline py-12 text-center">
      <div className="font-medium text-ink-dim">{title}</div>
      {hint ? <div className="mt-1 max-w-sm text-xs text-ink-faint">{hint}</div> : null}
    </div>
  );
}

export function JsonEvidence({ data }: { data: unknown }) {
  return (
    <pre className="mono max-h-72 overflow-auto rounded-lg border border-hairline bg-canvas p-3 text-xs leading-relaxed text-ink-dim">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}
