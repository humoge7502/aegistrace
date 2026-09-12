"use client";

import { useState } from "react";

import { Card, JsonEvidence, TrustBadge } from "@/components/ui";
import { fmtDate } from "@/lib/trust";

export default function CertificateCard({
  serial, status, issuedAt, statement,
}: {
  serial: string | null;
  status: string | null;
  issuedAt: string | null;
  statement: Record<string, unknown> | null;
}) {
  const [verify, setVerify] = useState<{ valid: boolean; reason: string } | null>(null);
  const [busy, setBusy] = useState(false);

  async function doVerify() {
    if (!serial) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/backend/certificates/${serial}/verify`, { method: "POST" });
      const body = await res.json();
      setVerify({ valid: body.valid, reason: body.reason });
    } catch {
      setVerify({ valid: false, reason: "verification request failed" });
    } finally {
      setBusy(false);
    }
  }

  if (!serial) {
    return (
      <Card title="AI Trust Certificate">
        <p className="text-sm text-ink-faint">
          No certificate — issued only for executions that pass all expected-state checks.
        </p>
      </Card>
    );
  }

  return (
    <Card title="AI Trust Certificate">
      <div className="relative overflow-hidden rounded-lg border-2 border-hairline bg-canvas p-4">
        {/* notched corner signature element */}
        <div className="absolute right-0 top-0 h-6 w-6 bg-surface" style={{ clipPath: "polygon(100% 0, 100% 100%, 0 0)" }} aria-hidden="true" />
        <div className="flex items-center justify-between">
          <span className="mono text-sm font-semibold text-accent">{serial}</span>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide ${
              status === "ACTIVE"
                ? "border-trust/40 bg-trust/10 text-trust"
                : "border-untrust/40 bg-untrust/10 text-untrust"
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: "currentColor" }} />
            {status ?? "—"}
          </span>
        </div>
        <div className="mt-1 text-[10px] text-ink-faint">issued {fmtDate(issuedAt)}</div>
        <p className="mono mt-3 break-all text-[10px] leading-relaxed text-ink-faint">
          ed25519 · in-toto Statement v1 · predicate aegistrace.dev/attestations/execution-trust/v1
        </p>
        <button
          onClick={doVerify}
          disabled={busy}
          className="mt-3 w-full rounded-lg border border-accent/40 bg-accent/10 py-1.5 text-xs font-semibold text-accent transition-colors hover:bg-accent/20 disabled:opacity-50"
        >
          {busy ? "Verifying…" : "Verify signature & revocation"}
        </button>
        {verify ? (
          <p
            role="status"
            className={`mt-2 rounded border px-2 py-1.5 text-xs ${
              verify.valid
                ? "border-trust/40 bg-trust/10 text-trust"
                : "border-untrust/40 bg-untrust/10 text-untrust"
            }`}
          >
            {verify.valid ? "VALID — " : "INVALID — "}
            {verify.reason}
          </p>
        ) : null}
      </div>
      {statement ? (
        <details className="mt-3">
          <summary className="cursor-pointer text-xs text-ink-faint">Signed statement (JSON)</summary>
          <div className="mt-2"><JsonEvidence data={statement} /></div>
        </details>
      ) : null}
    </Card>
  );
}
