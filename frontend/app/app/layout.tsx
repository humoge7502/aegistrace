import { redirect } from "next/navigation";

import { ConsoleMobileBar, ConsoleSidebar } from "@/components/ConsoleNav";
import { apiFetch, apiKeyOrNull } from "@/lib/api";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const key = await apiKeyOrNull();
  if (!key) redirect("/login");

  let auth: { role: string; tenant_id: string } | null = null;
  let backendError: string | null = null;
  try {
    auth = await apiFetch<{ role: string; tenant_id: string }>("/api/v1/auth/verify", {
      key,
      method: "POST",
    });
  } catch (e) {
    backendError = (e as { message?: string }).message ?? "backend unreachable";
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-[1500px]">
      <ConsoleSidebar role={auth?.role ?? null} />
      <div className="min-w-0 flex-1">
        <ConsoleMobileBar role={auth?.role ?? null} />
        {/* provenance rail (signature element) */}
        <div className="sticky top-0 z-20 hidden h-1.5 items-stretch bg-surface md:block" aria-hidden="true">
          <div className="state-pulse w-24 bg-gradient-to-r from-accent/70 to-transparent" />
          <div className="flex-1 border-b border-hairline" />
        </div>
        {backendError ? (
          <div className="mx-4 mt-4 rounded-lg border border-degraded/40 bg-degraded/10 px-4 py-3 text-sm text-degraded">
            Backend unreachable: {backendError}. Start it with{" "}
            <code className="mono">uvicorn backend.app.main:app --port 8420</code>.
          </div>
        ) : null}
        <main className="p-4 sm:p-6 lg:p-8">{children}</main>
        <footer className="mono border-t border-hairline px-4 py-4 text-[10px] text-ink-faint sm:px-6 lg:px-8">
          aegistrace console · v0.1.0 · unknown ≠ trusted
        </footer>
      </div>
    </div>
  );
}
