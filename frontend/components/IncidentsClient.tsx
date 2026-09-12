"use client";

import { useState } from "react";

import { JsonEvidence, SeverityBadge } from "@/components/ui";
import { fmtDate } from "@/lib/trust";

type Incident = {
  id: string; title: string; severity: string; status: string;
  description: string; evidence: Record<string, unknown>;
  created_at: string;
};

const STATUS_STYLES: Record<string, string> = {
  OPEN: "text-untrust border-untrust/40",
  CONTAINED: "text-quarantined border-quarantined/40",
  RECOVERING: "text-recovering border-recovering/40",
  RESOLVED: "text-trust border-trust/40",
};

export default function IncidentsClient({ rows }: { rows: Incident[] }) {
  const [local, setLocal] = useState(rows);
  const [open, setOpen] = useState<string | null>(rows[0]?.id ?? null);
  const [busy, setBusy] = useState(false);

  async function act(id: string, action: string) {
    const reason = action === "recover"
      ? window.prompt("Recovery note (e.g. digest restored & verified):") ?? "recovered"
      : `${action} by operator`;
    setBusy(true);
    try {
      const res = await fetch(`/api/backend/incidents/${id}/actions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, reason }),
      });
      const body = await res.json();
      if (res.ok) {
        setLocal((rs) => rs.map((r) => (r.id === id ? { ...r, status: body.status } : r)));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      {local.map((i) => {
        const expanded = open === i.id;
        return (
          <article key={i.id} className="rounded-[10px] border border-hairline bg-surface">
            <button
              className="flex w-full items-center gap-3 px-4 py-3 text-left"
              onClick={() => setOpen(expanded ? null : i.id)}
              aria-expanded={expanded}
            >
              <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${STATUS_STYLES[i.status] ?? "text-unknown border-unknown/40"}`}>
                {i.status}
              </span>
              <span className="min-w-0 flex-1 truncate text-sm font-medium">{i.title}</span>
              <SeverityBadge severity={i.severity} />
              <span className="hidden text-[10px] text-ink-faint sm:block">{fmtDate(i.created_at)}</span>
            </button>
            {expanded ? (
              <div className="space-y-3 border-t border-hairline px-4 py-3">
                <p className="text-sm text-ink-dim">{i.description}</p>
                <div className="flex flex-wrap gap-2">
                  {i.status !== "RESOLVED" ? (
                    <>
                      <button disabled={busy} onClick={() => act(i.id, "contain")} className="rounded border border-quarantined/40 bg-quarantined/10 px-3 py-1.5 text-xs font-medium text-quarantined disabled:opacity-40">Contain</button>
                      <button disabled={busy} onClick={() => act(i.id, "recover")} className="rounded border border-recovering/40 bg-recovering/10 px-3 py-1.5 text-xs font-medium text-recovering disabled:opacity-40">Recover…</button>
                      <button disabled={busy} onClick={() => act(i.id, "resolve")} className="rounded border border-trust/40 bg-trust/10 px-3 py-1.5 text-xs font-medium text-trust disabled:opacity-40">Resolve</button>
                    </>
                  ) : (
                    <span className="text-xs text-trust">Resolved {fmtDate(i.created_at)}</span>
                  )}
                </div>
                <details>
                  <summary className="cursor-pointer text-xs text-ink-faint">Propagation evidence</summary>
                  <div className="mt-2"><JsonEvidence data={i.evidence} /></div>
                </details>
              </div>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}
