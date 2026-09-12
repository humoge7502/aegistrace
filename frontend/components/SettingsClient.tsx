"use client";

import { useState } from "react";

export default function SettingsClient() {
  const [name, setName] = useState("");
  const [role, setRole] = useState("agent");
  const [created, setCreated] = useState<{ key: string; role: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function createKey(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/backend/auth/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, role }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(typeof body.detail === "string" ? body.detail : "creation failed (admin role required)");
        return;
      }
      setCreated({ key: body.key, role: body.role });
      setName("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <form onSubmit={createKey} className="flex flex-wrap gap-2">
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="key name (e.g. ci-collector)"
          className="min-w-40 flex-1 rounded-lg border border-hairline bg-canvas px-3 py-2 text-sm outline-none placeholder:text-ink-faint focus:border-accent/60"
        />
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="rounded-lg border border-hairline bg-canvas px-3 py-2 text-sm outline-none focus:border-accent/60"
          aria-label="Role"
        >
          <option value="agent">agent (ingest-only)</option>
          <option value="viewer">viewer</option>
          <option value="operator">operator</option>
          <option value="admin">admin</option>
        </select>
        <button
          type="submit"
          disabled={busy}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-canvas disabled:opacity-50"
        >
          {busy ? "…" : "Create"}
        </button>
      </form>
      {error ? <p role="alert" className="mt-2 text-xs text-untrust">{error}</p> : null}
      {created ? (
        <div className="mt-3 rounded-lg border border-accent/40 bg-accent/5 p-3">
          <div className="microlabel text-accent">key created — copy now, shown once</div>
          <code className="mono mt-1 block break-all text-xs text-ink">{created.key}</code>
          <div className="mt-1 text-[10px] text-ink-faint">role: {created.role} · hashed server-side (sha256)</div>
        </div>
      ) : null}
      <p className="mt-3 text-xs leading-relaxed text-ink-faint">
        Roles: <b>agent</b> may only ingest events; <b>viewer</b> read-only;
        <b> operator</b> may compromise/recover components and act on incidents;
        <b> admin</b> manages keys, policies and the audit log.
      </p>
    </div>
  );
}
