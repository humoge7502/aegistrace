"use client";

import Link from "next/link";
import { useState } from "react";

import { TrustBadge } from "@/components/ui";

function CertStatusBadge({ status }: { status: string }) {
  const active = status === "ACTIVE";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide ${
        active ? "border-trust/40 bg-trust/10 text-trust" : "border-untrust/40 bg-untrust/10 text-untrust"
      }`}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: "currentColor" }} />
      {status}
    </span>
  );
}
import { fmtDate } from "@/lib/trust";

type CertRow = {
  id: string; serial: string; execution_id: string; status: string;
  alg: string; key_id: string; issued_at: string; revoked_reason: string | null;
};

export default function CertificatesClient({ rows }: { rows: CertRow[] }) {
  const [results, setResults] = useState<Record<string, { valid: boolean; reason: string }>>({});
  const [busy, setBusy] = useState<string | null>(null);

  async function verify(serial: string) {
    setBusy(serial);
    try {
      const res = await fetch(`/api/backend/certificates/${serial}/verify`, { method: "POST" });
      const body = await res.json();
      setResults((r) => ({ ...r, [serial]: { valid: body.valid, reason: body.reason } }));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="overflow-x-auto rounded-[10px] border border-hairline bg-surface">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-hairline text-left">
            <th className="microlabel px-3 py-2">Serial</th>
            <th className="microlabel px-3 py-2">Status</th>
            <th className="microlabel px-3 py-2">Issued</th>
            <th className="microlabel px-3 py-2">Key</th>
            <th className="microlabel px-3 py-2">Verification</th>
            <th className="microlabel px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.id} className="border-b border-hairline/50 last:border-0">
              <td className="mono px-3 py-2.5 text-accent">{c.serial}</td>
              <td className="px-3 py-2.5">
                <CertStatusBadge status={c.status} />
                {c.revoked_reason ? (
                  <div className="mt-1 max-w-52 truncate text-[10px] text-ink-faint" title={c.revoked_reason}>
                    {c.revoked_reason}
                  </div>
                ) : null}
              </td>
              <td className="px-3 py-2.5 text-xs text-ink-faint">{fmtDate(c.issued_at)}</td>
              <td className="mono px-3 py-2.5 text-xs text-ink-dim">{c.alg} · {c.key_id}</td>
              <td className="px-3 py-2.5 text-xs">
                {results[c.serial] ? (
                  <span className={results[c.serial].valid ? "text-trust" : "text-untrust"}>
                    {results[c.serial].valid ? "VALID" : "INVALID"} — {results[c.serial].reason}
                  </span>
                ) : (
                  <span className="text-ink-faint">not verified</span>
                )}
              </td>
              <td className="px-3 py-2.5 text-right">
                <div className="flex justify-end gap-1.5">
                  <button
                    onClick={() => verify(c.serial)}
                    disabled={busy === c.serial}
                    className="rounded border border-accent/40 bg-accent/10 px-2 py-1 text-[10px] font-semibold text-accent disabled:opacity-40"
                  >
                    verify
                  </button>
                  <Link
                    href={`/app/executions/${c.execution_id}`}
                    className="rounded border border-hairline px-2 py-1 text-[10px] text-ink-dim hover:text-ink"
                  >
                    execution
                  </Link>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
