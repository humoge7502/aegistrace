"use client";

import { useState } from "react";

import { Card, TrustBadge } from "@/components/ui";
import { fmtDate, shortDigest } from "@/lib/trust";

type ComponentRow = {
  id: string; kind: string; name: string; version: string | null;
  digest_expected: string | null; digest_observed: string | null;
  trust_state: string; state_reason: string | null; state_updated_at: string;
};

type Impact = {
  component: { name: string; trust_state: string };
  executions: { execution_id: string; external_id: string; trust_state: string; agent_ref: string }[];
  outputs: { output_id: string; external_id: string; trust_state: string; quarantined: boolean }[];
  certificates: { serial: string; status: string; revoked_reason: string | null }[];
};

export default function ComponentsClient({ rows }: { rows: ComponentRow[] }) {
  const [local, setLocal] = useState(rows);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [impact, setImpact] = useState<Impact | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function changeTrust(id: string, state: "COMPROMISED" | "TRUSTED") {
    const reason = state === "COMPROMISED"
      ? window.prompt("Reason for marking COMPROMISED? (recorded as evidence)")
      : "restored to trusted digest (operator recovery)";
    if (!reason) return;
    setBusyId(id);
    setError(null);
    try {
      const res = await fetch(`/api/backend/components/${id}/trust`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, reason }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body.detail ?? `HTTP ${res.status}`);
        return;
      }
      setLocal((rs) => rs.map((r) => (r.id === id
        ? { ...r, trust_state: state, state_reason: reason }
        : r)));
      if (state === "COMPROMISED" && body.affected_executions) {
        window.alert(
          `Propagation complete:\n· executions invalidated: ${body.affected_executions.length}\n` +
          `· outputs quarantined: ${body.affected_outputs.length}\n` +
          `· certificates revoked: ${body.revoked_certificates.length}`,
        );
      }
    } finally {
      setBusyId(null);
    }
  }

  async function showImpact(id: string) {
    setBusyId(id);
    setError(null);
    try {
      const res = await fetch(`/api/backend/components/${id}/impact`);
      setImpact(await res.json());
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-3">
      <div className="min-w-0 xl:col-span-2">
        <Card title={`${local.length} components`}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-hairline text-left">
                  <th className="microlabel px-3 py-2">Component</th>
                  <th className="microlabel px-3 py-2">Kind</th>
                  <th className="microlabel px-3 py-2">Digest</th>
                  <th className="microlabel px-3 py-2">State</th>
                  <th className="microlabel px-3 py-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {local.map((r) => (
                  <tr key={r.id} className="border-b border-hairline/50 last:border-0 hover:bg-surface-2">
                    <td className="px-3 py-2.5">
                      <div className="mono truncate font-medium" title={r.name}>{r.name}</div>
                      {r.version ? <div className="text-[10px] text-ink-faint">v{r.version}</div> : null}
                    </td>
                    <td className="px-3 py-2.5 text-xs text-ink-dim">{r.kind}</td>
                    <td className="mono px-3 py-2.5 text-[11px] text-ink-faint">
                      <span className="block whitespace-nowrap" title={`expected ${r.digest_expected ?? "—"}`}>
                        exp {shortDigest(r.digest_expected)}
                      </span>
                      <span className="block whitespace-nowrap" title={`observed ${r.digest_observed ?? "—"}`}>
                        obs {shortDigest(r.digest_observed)}
                      </span>
                    </td>
                    <td className="px-3 py-2.5"><TrustBadge state={r.trust_state} small /></td>
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex justify-end gap-1.5">
                        <button
                          className="rounded border border-hairline px-2 py-1 text-[10px] text-ink-dim hover:text-ink disabled:opacity-40"
                          disabled={busyId === r.id}
                          onClick={() => showImpact(r.id)}
                        >
                          impact
                        </button>
                        {r.trust_state === "COMPROMISED" ? (
                          <button
                            className="rounded border border-recovering/40 bg-recovering/10 px-2 py-1 text-[10px] text-recovering disabled:opacity-40"
                            disabled={busyId === r.id}
                            onClick={() => changeTrust(r.id, "TRUSTED")}
                          >
                            recover
                          </button>
                        ) : (
                          <button
                            className="rounded border border-untrust/40 bg-untrust/10 px-2 py-1 text-[10px] text-untrust disabled:opacity-40"
                            disabled={busyId === r.id}
                            onClick={() => changeTrust(r.id, "COMPROMISED")}
                          >
                            compromise
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {local.length === 0 ? (
                  <tr><td colSpan={5} className="px-3 py-8 text-center text-sm text-ink-faint">No components observed yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
          {error ? <p role="alert" className="mt-3 text-xs text-untrust">{error}</p> : null}
        </Card>
      </div>

      <div className="min-w-0">
        <Card title="Dependency impact (live)">
          {impact ? (
            <div className="space-y-3">
              <div className="mono text-sm">{impact.component.name}</div>
              <TrustBadge state={impact.component.trust_state} small />
              <div className="text-xs text-ink-dim">
                {impact.executions.length} execution(s) · {impact.outputs.length} output(s) ·{" "}
                {impact.certificates.length} certificate(s)
              </div>
              <ul className="space-y-1">
                {impact.executions.map((e) => (
                  <li key={e.execution_id} className="flex items-center justify-between rounded border border-hairline bg-surface-2 px-2 py-1.5 text-xs">
                    <span className="mono truncate">{e.external_id}</span>
                    <TrustBadge state={e.trust_state} small />
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-sm text-ink-faint">
              Select “impact” on a component to see which executions, outputs and
              certificates depend on it — the answer to “what else was affected?”.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
