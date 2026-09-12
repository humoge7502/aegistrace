"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginForm() {
  const router = useRouter();
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ apiKey }),
      });
      const body = await res.json();
      if (!res.ok || !body.ok) {
        setError(body.error ?? "sign-in failed");
        return;
      }
      router.push("/app");
    } catch {
      setError("could not reach the sign-in endpoint");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="mt-7 rounded-[10px] border border-hairline bg-surface p-5">
      <label htmlFor="apiKey" className="microlabel">API key</label>
      <input
        id="apiKey"
        type="password"
        autoComplete="off"
        required
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="at_…"
        aria-describedby={error ? "login-error" : undefined}
        className="mono mt-2 w-full rounded-lg border border-hairline bg-canvas px-3 py-2.5 text-sm outline-none transition-colors placeholder:text-ink-faint focus:border-accent/60"
      />
      {error ? (
        <p id="login-error" role="alert" className="mt-3 rounded-lg border border-untrust/40 bg-untrust/10 px-3 py-2 text-xs text-untrust">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={busy}
        className="mt-4 w-full rounded-lg bg-accent py-2.5 text-sm font-semibold text-canvas transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {busy ? "Verifying…" : "Sign in"}
      </button>
      <p className="mono mt-4 text-center text-[10px] text-ink-faint">
        keys validated server-side · httpOnly cookie · no client-side secrets
      </p>
    </form>
  );
}
