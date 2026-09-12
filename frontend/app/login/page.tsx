import Link from "next/link";
import type { Metadata } from "next";

import { AegisMark } from "@/components/landing/SiteHeader";
import { themeInitScript } from "@/components/theme";
import LoginForm from "@/components/LoginForm";

export const metadata: Metadata = {
  title: "Sign in",
  description: "Sign in to the AegisTrace console with your API key.",
};

export default function LoginPage() {
  return (
    <main id="main" className="grid min-h-screen lg:grid-cols-2">
      {/* editorial panel */}
      <aside className="relative hidden flex-col justify-between overflow-hidden border-r border-hairline bg-canvas-2 p-10 lg:flex">
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <div className="dotgrid pointer-events-none absolute inset-0 opacity-40" aria-hidden="true" />
        <div className="relative">
          <Link href="/" className="flex items-center gap-2.5" aria-label="AegisTrace home">
            <AegisMark />
            <span className="display text-lg tracking-tight">AegisTrace</span>
          </Link>
        </div>
        <div className="relative max-w-md">
          <p className="microlabel">runtime causal trust</p>
          <p className="display-md mt-5 text-balance">
            The console shows the causal truth of every AI execution your
            agents have run.
          </p>
          <ul className="mono mt-8 space-y-2 text-[11px] text-ink-faint">
            <li>· expected-vs-observed verification per run</li>
            <li>· compromise propagation with evidence chains</li>
            <li>· verifiable AI Trust Certificates (ed25519)</li>
          </ul>
        </div>
        <p className="mono relative text-[10px] text-ink-faint">
          unknown ≠ trusted
        </p>
      </aside>

      {/* form panel */}
      <div className="flex items-center justify-center px-5 py-16 sm:px-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Link href="/" className="flex items-center gap-2.5" aria-label="AegisTrace home">
              <AegisMark />
              <span className="display text-lg tracking-tight">AegisTrace</span>
            </Link>
          </div>
          <h1 className="display-md">Sign in</h1>
          <p className="mt-2 text-sm leading-relaxed text-ink-dim">
            Use a per-tenant API key. The bootstrap admin key is printed once
            when the backend first starts; agent keys (ingest-only) cannot
            read the console.
          </p>
          <LoginForm />
        </div>
      </div>
    </main>
  );
}
