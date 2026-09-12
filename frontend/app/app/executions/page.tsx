import Link from "next/link";

import { apiFetch } from "@/lib/api";
import { Card, EmptyState, TrustBadge } from "@/components/ui";
import { fmtDate } from "@/lib/trust";

type ExecutionRow = {
  id: string;
  external_id: string;
  agent_ref: string;
  agent_version: string | null;
  status: string;
  trust_state: string;
  started_at: string;
  finished_at: string | null;
};

export default async function ExecutionsPage() {
  let rows: ExecutionRow[];
  try {
    rows = await apiFetch<ExecutionRow[]>("/api/v1/executions");
  } catch (e) {
    return <EmptyState title="Could not load executions" hint={(e as { message?: string }).message} />;
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">Executions</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Every attested agent run. Click one for its AI Execution Passport and causal graph.
        </p>
      </header>

      {rows.length === 0 ? (
        <EmptyState
          title="No executions recorded"
          hint="Run `python demo/killer_demo.py` with the backend up, or instrument your agent with the SDK."
        />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-hairline text-left">
                  <th className="microlabel px-3 py-2">Run</th>
                  <th className="microlabel px-3 py-2">Agent</th>
                  <th className="microlabel px-3 py-2">Status</th>
                  <th className="microlabel px-3 py-2">Trust state</th>
                  <th className="microlabel px-3 py-2">Started</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-hairline/50 transition-colors last:border-0 hover:bg-surface-2">
                    <td className="px-3 py-2.5">
                      <Link className="mono text-accent hover:underline" href={`/app/executions/${r.id}`}>
                        {r.external_id}
                      </Link>
                    </td>
                    <td className="px-3 py-2.5 text-ink-dim">
                      {r.agent_ref}
                      {r.agent_version ? <span className="mono text-ink-faint"> @{r.agent_version}</span> : null}
                    </td>
                    <td className="px-3 py-2.5 text-ink-dim">{r.status}</td>
                    <td className="px-3 py-2.5"><TrustBadge state={r.trust_state} small /></td>
                    <td className="px-3 py-2.5 text-xs text-ink-faint">{fmtDate(r.started_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
