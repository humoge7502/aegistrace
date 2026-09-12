import Link from "next/link";
import { redirect } from "next/navigation";

import { apiFetch, apiKeyOrNull } from "@/lib/api";
import { TrustBadge } from "@/components/ui";

const NAV = [
  { href: "/app", label: "Overview", glyph: "◈" },
  { href: "/app/executions", label: "Executions", glyph: "≣" },
  { href: "/app/components", label: "Components", glyph: "⬡" },
  { href: "/app/incidents", label: "Incidents", glyph: "▲" },
  { href: "/app/certificates", label: "Certificates", glyph: "✓" },
  { href: "/app/attackbench", label: "AttackBench", glyph: "◎" },
  { href: "/app/settings", label: "Settings", glyph: "⚙" },
];

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const key = await apiKeyOrNull();
  if (!key) redirect("/login");

  let auth: { role: string; tenant_id: string } | null = null;
  let backendError: string | null = null;
  try {
    auth = await apiFetch<{ role: string; tenant_id: string }>("/api/v1/auth/verify", { key, method: "POST" });
  } catch (e) {
    backendError = (e as { message?: string }).message ?? "backend unreachable";
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-[1500px]">
      {/* sidebar */}
      <aside className="sticky top-0 hidden h-screen w-56 shrink-0 flex-col border-r border-hairline bg-surface md:flex">
        <Link href="/" className="flex items-center gap-2.5 border-b border-hairline px-4 py-4">
          <svg width="22" height="22" viewBox="0 0 26 26" aria-hidden="true">
            <path d="M13 1.5 23 5.5v7c0 6-4.4 10.4-10 12C7.4 22.9 3 18.5 3 12.5v-7L13 1.5Z" fill="#22d3ee" fillOpacity="0.12" stroke="#22d3ee" strokeWidth="1.5" />
            <path d="M8 13.2l3.4 3.4L18.5 9.5" stroke="#22d3ee" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="font-bold tracking-tight">AegisTrace</span>
        </Link>
        <nav className="flex-1 space-y-0.5 p-2" aria-label="Console">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-ink-dim transition-colors hover:bg-surface-2 hover:text-ink"
            >
              <span className="w-4 text-center text-ink-faint" aria-hidden="true">{item.glyph}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-hairline p-4">
          {auth ? (
            <>
              <div className="microlabel">role</div>
              <div className="mono mt-1 text-xs text-ink-dim">{auth.role}</div>
            </>
          ) : null}
          <form action="/api/logout" method="post" className="mt-3">
            <button className="w-full rounded-lg border border-hairline px-3 py-1.5 text-xs text-ink-dim transition-colors hover:text-ink" type="submit">
              Sign out
            </button>
          </form>
        </div>
      </aside>

      {/* main */}
      <div className="min-w-0 flex-1">
        {/* provenance rail (signature element) */}
        <div className="sticky top-0 z-10 flex h-1.5 items-stretch bg-surface" aria-hidden="true">
          <div className="state-pulse w-24 bg-gradient-to-r from-accent/70 to-transparent" />
          <div className="flex-1 border-b border-hairline" />
        </div>
        {/* mobile nav */}
        <div className="flex gap-1 overflow-x-auto border-b border-hairline px-3 py-2 md:hidden">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="whitespace-nowrap rounded-lg px-3 py-1.5 text-xs text-ink-dim hover:bg-surface-2">
              {item.label}
            </Link>
          ))}
        </div>
        {backendError ? (
          <div className="mx-4 mt-4 rounded-lg border border-degraded/40 bg-degraded/10 px-4 py-3 text-sm text-degraded">
            Backend unreachable: {backendError}. Start it with{" "}
            <code className="mono">uvicorn backend.app.main:app --port 8420</code>.
          </div>
        ) : null}
        <main className="p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
