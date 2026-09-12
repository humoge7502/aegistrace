"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { AegisMark } from "@/components/landing/SiteHeader";
import { useTheme } from "@/components/theme";

const NAV = [
  { href: "/app", label: "Overview", glyph: "◈" },
  { href: "/app/executions", label: "Executions", glyph: "≣" },
  { href: "/app/components", label: "Components", glyph: "⬡" },
  { href: "/app/incidents", label: "Incidents", glyph: "▲" },
  { href: "/app/certificates", label: "Certificates", glyph: "✓" },
  { href: "/app/attackbench", label: "AttackBench", glyph: "◎" },
  { href: "/app/settings", label: "Settings", glyph: "⚙" },
];

function isActive(pathname: string, href: string): boolean {
  return href === "/app" ? pathname === "/app" : pathname.startsWith(href);
}

function ThemeButton() {
  const { theme, toggle } = useTheme();
  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={theme === "paper" ? "Switch to dark ledger theme" : "Switch to paper theme"}
      className="flex h-8 w-8 items-center justify-center rounded-lg border border-hairline text-ink-dim transition-colors hover:border-ink-faint hover:text-ink"
    >
      {theme === "paper" ? (
        <svg width="13" height="13" viewBox="0 0 15 15" fill="none" aria-hidden="true">
          <path d="M7.5 10.5a3 3 0 100-6 3 3 0 000 6ZM7.5 0v2M7.5 13v2M15 7.5h-2M2 7.5H0M12.6 2.4l-1.4 1.4M3.8 11.2l-1.4 1.4M12.6 12.6l-1.4-1.4M3.8 3.8 2.4 2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
      ) : (
        <svg width="13" height="13" viewBox="0 0 15 15" fill="none" aria-hidden="true">
          <path d="M13 9.2A6 6 0 015.8 2 6 6 0 108.5 14a6 6 0 004.5-4.8Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
        </svg>
      )}
    </button>
  );
}

export function ConsoleSidebar({ role }: { role: string | null }) {
  const pathname = usePathname();
  return (
    <aside className="sticky top-0 hidden h-screen w-56 shrink-0 flex-col border-r border-hairline bg-surface md:flex">
      <Link href="/" className="flex items-center gap-2.5 border-b border-hairline px-4 py-4">
        <AegisMark size={22} />
        <span className="display tracking-tight">AegisTrace</span>
      </Link>
      <nav aria-label="Console" className="flex-1 space-y-0.5 p-2">
        {NAV.map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-accent/10 font-semibold text-accent"
                  : "text-ink-dim hover:bg-surface-2 hover:text-ink"
              }`}
            >
              <span className="w-4 text-center" aria-hidden="true">{item.glyph}</span>
              {item.label}
              {active ? <span className="ml-auto h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" /> : null}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-hairline p-4">
        {role ? (
          <>
            <div className="microlabel">role</div>
            <div className="mono mt-1 text-xs text-ink-dim">{role}</div>
          </>
        ) : null}
        <div className="mt-3 flex items-center gap-2">
          <ThemeButton />
          <form action="/api/logout" method="post" className="flex-1">
            <button className="w-full rounded-lg border border-hairline px-3 py-1.5 text-xs text-ink-dim transition-colors hover:text-ink" type="submit">
              Sign out
            </button>
          </form>
        </div>
      </div>
    </aside>
  );
}

export function ConsoleMobileBar({ role }: { role: string | null }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  return (
    <div className="sticky top-0 z-40 border-b border-hairline bg-canvas/90 backdrop-blur-md md:hidden">
      <div className="flex items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2" aria-label="AegisTrace home">
          <AegisMark size={20} />
          <span className="display tracking-tight">AegisTrace</span>
        </Link>
        <div className="flex items-center gap-2">
          <ThemeButton />
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? "Close navigation" : "Open navigation"}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-hairline text-ink-dim"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              {open ? (
                <path d="M2 2l10 10M12 2 2 12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              ) : (
                <path d="M1 3.5h12M1 7h12M1 10.5h12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              )}
            </svg>
          </button>
        </div>
      </div>
      {open ? (
        <nav id="mobile-nav" aria-label="Console" className="border-t border-hairline bg-surface px-3 py-2">
          {NAV.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm ${
                  active ? "bg-accent/10 font-semibold text-accent" : "text-ink-dim"
                }`}
              >
                <span className="w-4 text-center" aria-hidden="true">{item.glyph}</span>
                {item.label}
              </Link>
            );
          })}
          <form action="/api/logout" method="post" className="p-1">
            <button className="w-full rounded-lg border border-hairline px-3 py-2 text-xs text-ink-dim" type="submit">
              Sign out{role ? ` (${role})` : ""}
            </button>
          </form>
        </nav>
      ) : null}
    </div>
  );
}
