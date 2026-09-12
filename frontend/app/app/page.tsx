import Link from "next/link";

import { apiFetch } from "@/lib/api";
import { Card, EmptyState, SeverityBadge, StatTile, TrustBadge } from "@/components/ui";
import { fmtDate } from "@/lib/trust";

type Overview = {
  executions_total: number;
  executions_by_trust_state: Record<string, number>;
  components_total: number;
  components_by_trust_state: Record<string, number>;
  open_incidents: { id: string; title: string; severity: string; status: string }[];
  recent_integrity_events: {
    id: string; kind: string; severity: string; title: string;
    created_at: string; execution_id: string | null;
  }[];
};

const STATE_ORDER = ["TRUSTED", "RE-CERTIFIED", "DEGRADED", "UNKNOWN", "QUARANTINED", "UNTRUSTED", "COMPROMISED"];

export default async function OverviewPage() {
  let data: Overview;
  try {
    data = await apiFetch<Overview>("/api/v1/overview");
  } catch (e) {
    return <EmptyState title="Could not load overview" hint={(e as { message?: string }).message} />;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-xl font-bold tracking-tight">Trust overview</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Live trust posture across all executions and components in this tenant.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile label="Executions" value={data.executions_total} />
        <StatTile label="Components" value={data.components_total} />
        <StatTile label="Open incidents" value={data.open_incidents.length} state="COMPROMISED" />
        <StatTile
          label="Untrusted outputs"
          value={(data.executions_by_trust_state["UNTRUSTED"] ?? 0)}
          state="UNTRUSTED"
          hint="executions"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Executions by trust state">
          <div className="space-y-2">
            {STATE_ORDER.filter((s) => data.executions_by_trust_state[s]).length === 0 ? (
              <p className="text-sm text-ink-faint">No executions yet — run the demo to populate.</p>
            ) : (
              STATE_ORDER.filter((s) => data.executions_by_trust_state[s]).map((state) => {
                const count = data.executions_by_trust_state[state];
                const pct = data.executions_total ? Math.round((count / data.executions_total) * 100) : 0;
                return (
                  <div key={state} className="flex items-center gap-3">
                    <div className="w-32"><TrustBadge state={state} small /></div>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-2">
                      <div className="h-full rounded-full bg-current opacity-60"
                        style={{ width: `${pct}%`, color: "inherit" }}
                      />
                    </div>
                    <span className="mono w-12 text-right text-xs text-ink-dim">{count}</span>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        <Card title="Components by trust state">
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.components_by_trust_state).length === 0 ? (
              <p className="text-sm text-ink-faint">No components observed yet.</p>
            ) : (
              Object.entries(data.components_by_trust_state)
                .sort((a, b) => b[1] - a[1])
                .map(([state, count]) => (
                  <span key={state} className="flex items-center gap-2 rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                    <TrustBadge state={state} small />
                    <span className="mono text-sm">{count}</span>
                  </span>
                ))
            )}
          </div>
        </Card>

        <Card title="Open incidents" action={<Link className="text-xs text-accent" href="/app/incidents">view all →</Link>}>
          {data.open_incidents.length === 0 ? (
            <p className="text-sm text-ink-faint">No open incidents.</p>
          ) : (
            <ul className="space-y-2">
              {data.open_incidents.map((i) => (
                <li key={i.id} className="flex items-center justify-between rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                  <span className="truncate text-sm">{i.title}</span>
                  <TrustBadge state={i.status === "CONTAINED" ? "QUARANTINED" : "RECOVERING"} small />
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Recent integrity events">
          {data.recent_integrity_events.length === 0 ? (
            <p className="text-sm text-ink-faint">No deviations observed.</p>
          ) : (
            <ul className="space-y-2">
              {data.recent_integrity_events.slice(0, 6).map((e) => (
                <li key={e.id} className="rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={e.severity} />
                    <span className="mono text-xs text-ink-faint">{e.kind}</span>
                    <span className="ml-auto text-[10px] text-ink-faint">{fmtDate(e.created_at)}</span>
                  </div>
                  <div className="mt-1 text-sm">{e.title}</div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
