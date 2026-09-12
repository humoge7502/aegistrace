export type TrustState =
  | "TRUSTED"
  | "UNTRUSTED"
  | "UNKNOWN"
  | "DEGRADED"
  | "COMPROMISED"
  | "QUARANTINED"
  | "RECOVERING"
  | "RE-CERTIFIED";

export const TRUST_COLORS: Record<TrustState, { text: string; bg: string; border: string; hex: string }> = {
  TRUSTED: { text: "text-trust", bg: "bg-trust/10", border: "border-trust/40", hex: "var(--color-trust)" },
  UNTRUSTED: { text: "text-untrust", bg: "bg-untrust/10", border: "border-untrust/40", hex: "var(--color-untrust)" },
  UNKNOWN: { text: "text-unknown", bg: "bg-unknown/10", border: "border-unknown/40", hex: "var(--color-unknown)" },
  DEGRADED: { text: "text-degraded", bg: "bg-degraded/10", border: "border-degraded/40", hex: "var(--color-degraded)" },
  COMPROMISED: { text: "text-compromised", bg: "bg-compromised/15", border: "border-compromised/50", hex: "var(--color-compromised)" },
  QUARANTINED: { text: "text-quarantined", bg: "bg-quarantined/10", border: "border-quarantined/40", hex: "var(--color-quarantined)" },
  RECOVERING: { text: "text-recovering", bg: "bg-recovering/10", border: "border-recovering/40", hex: "var(--color-recovering)" },
  "RE-CERTIFIED": { text: "text-recertified", bg: "bg-recertified/10", border: "border-recertified/40", hex: "var(--color-recertified)" },
};

export function stateColor(state: string): string {
  return (TRUST_COLORS[state as TrustState] ?? TRUST_COLORS.UNKNOWN).hex;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** Deterministic, locale-independent formatting (server == client). */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${pad(d.getDate())} ${MONTHS[d.getMonth()]} ${d.getFullYear()}, ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  );
}

export function shortDigest(d: string | null | undefined): string {
  if (!d) return "—";
  return d.length > 20 ? `${d.slice(0, 12)}…${d.slice(-6)}` : d;
}

export const SEVERITY_ORDER: Record<string, number> = {
  info: 0, low: 1, medium: 2, high: 3, critical: 4,
};
