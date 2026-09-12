"use client";

import Link from "next/link";

import { useTheme } from "@/components/theme";

const NAV = [
  { href: "/#thesis", label: "Thesis" },
  { href: "/#system", label: "System" },
  { href: "/#evidence", label: "Evidence" },
];

export function AegisMark({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 26 26" aria-hidden="true">
      <path
        d="M13 1.5 23 5.5v7c0 6-4.4 10.4-10 12C7.4 22.9 3 18.5 3 12.5v-7L13 1.5Z"
        fill="var(--color-accent)"
        fillOpacity="0.12"
        stroke="var(--color-accent)"
        strokeWidth="1.5"
      />
      <path
        d="M8 13.2l3.4 3.4L18.5 9.5"
        stroke="var(--color-accent)"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function SiteHeader() {
  const { theme, toggle } = useTheme();
  return (
    <header className="rule-b sticky top-0 z-40 bg-canvas/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
        <Link href="/" className="flex items-center gap-2.5" aria-label="AegisTrace home">
          <AegisMark />
          <span className="display text-lg tracking-tight">AegisTrace</span>
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-7 md:flex">
          {NAV.map((item) => (
            <a key={item.href} href={item.href} className="navlink text-sm text-ink-dim transition-colors hover:text-ink">
              {item.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={toggle}
            aria-label={theme === "paper" ? "Switch to dark ledger theme" : "Switch to paper theme"}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-hairline text-ink-dim transition-colors hover:border-ink-faint hover:text-ink"
          >
            {theme === "paper" ? (
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
                <path d="M7.5 10.5a3 3 0 100-6 3 3 0 000 6Z M7.5 0v2M7.5 13v2M15 7.5h-2M2 7.5H0M12.6 2.4l-1.4 1.4M3.8 11.2l-1.4 1.4M12.6 12.6l-1.4-1.4M3.8 3.8 2.4 2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
                <path d="M13 9.2A6 6 0 015.8 2 6 6 0 108.5 14a6 6 0 004.5-4.8Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
              </svg>
            )}
          </button>
          <Link
            href="/login"
            className="rounded-lg border border-accent/40 bg-accent/10 px-4 py-2 text-sm font-semibold text-accent transition-colors hover:bg-accent/20"
          >
            Open console
          </Link>
        </div>
      </div>
    </header>
  );
}
