"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
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
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="microlabel">aegistrace console</div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight">Sign in with an API key</h1>
          <p className="mt-2 text-sm text-ink-dim">
            Keys are issued per tenant (<span className="mono">POST /api/v1/auth/keys</span>).
            The bootstrap admin key is printed once when the backend first starts.
          </p>
        </div>
        <form onSubmit={submit} className="rounded-[10px] border border-hairline bg-surface p-5">
          <label htmlFor="apiKey" className="microlabel">API key</label>
          <input
            id="apiKey"
            type="password"
            autoComplete="off"
            required
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="at_..."
            className="mono mt-2 w-full rounded-lg border border-hairline bg-canvas px-3 py-2.5 text-sm outline-none transition-colors placeholder:text-ink-faint focus:border-accent/60"
          />
          {error ? (
            <p role="alert" className="mt-3 rounded-lg border border-untrust/40 bg-untrust/10 px-3 py-2 text-xs text-untrust">
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
        </form>
        <p className="mt-4 text-center text-xs text-ink-faint">
          Keys are validated server-side and stored in an httpOnly cookie.
        </p>
      </div>
    </main>
  );
}
