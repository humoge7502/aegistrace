"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Unhandled UI error:", error);
  }, [error]);

  return (
    <main id="main" className="flex min-h-screen items-center justify-center px-5">
      <div className="w-full max-w-md text-center">
        <p className="microlabel">system fault</p>
        <h1 className="display-lg mt-4">This page failed to render.</h1>
        <p className="mt-4 text-sm leading-relaxed text-ink-dim">
          The error was logged. You can retry the page — if it persists, check
          that the backend is reachable and reload.
        </p>
        {error.digest ? (
          <p className="mono mt-3 text-[10px] text-ink-faint">digest: {error.digest}</p>
        ) : null}
        <div className="mt-8 flex justify-center gap-3">
          <button
            onClick={reset}
            className="rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
          >
            Try again
          </button>
          <Link
            href="/"
            className="rounded-lg border border-hairline px-5 py-2.5 text-sm text-ink-dim transition-colors hover:text-ink"
          >
            Back to safety
          </Link>
        </div>
      </div>
    </main>
  );
}
