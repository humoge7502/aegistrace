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
  TRUSTED: { text: "text-trust", bg: "bg-trust/10", border: "border-trust/40", hex: "#4ade80" },
  UNTRUSTED: { text: "text-untrust", bg: "bg-untrust/10", border: "border-untrust/40", hex: "#f87171" },
  UNKNOWN: { text: "text-unknown", bg: "bg-unknown/10", border: "border-unknown/40", hex: "#94a3b8" },
  DEGRADED: { text: "text-degraded", bg: "bg-degraded/10", border: "border-degraded/40", hex: "#fbbf24" },
  COMPROMISED: { text: "text-compromised", bg: "bg-compromised/15", border: "border-compromised/50", hex: "#fda4af" },
  QUARANTINED: { text: "text-quarantined", bg: "bg-quarantined/10", border: "border-quarantined/40", hex: "#fb923c" },
  RECOVERING: { text: "text-recovering", bg: "bg-recovering/10", border: "border-recovering/40", hex: "#60a5fa" },
  "RE-CERTIFIED": { text: "text-recertified", bg: "bg-recertified/10", border: "border-recertified/40", hex: "#2dd4bf" },
};

export function stateColor(state: string): string {
  return (TRUST_COLORS[state as TrustState] ?? TRUST_COLORS.UNKNOWN).hex;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    year: "numeric", month: "short", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

export function shortDigest(d: string | null | undefined): string {
  if (!d) return "—";
  return d.length > 20 ? `${d.slice(0, 12)}…${d.slice(-6)}` : d;
}

export const SEVERITY_ORDER: Record<string, number> = {
  info: 0, low: 1, medium: 2, high: 3, critical: 4,
};
