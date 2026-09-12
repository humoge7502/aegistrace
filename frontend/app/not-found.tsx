import Link from "next/link";

export default function NotFound() {
  return (
    <main id="main" className="flex min-h-screen items-center justify-center px-5">
      <div className="w-full max-w-md text-center">
        <p className="microlabel">404 · not in the ledger</p>
        <h1 className="display-lg mt-4">Nothing was recorded here.</h1>
        <p className="mt-4 text-sm leading-relaxed text-ink-dim">
          The page you requested does not exist. If you followed a link to an
          execution or component, it may belong to another tenant — or never
          happened at all.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link
            href="/app"
            className="rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-canvas transition-opacity hover:opacity-90"
          >
            Console overview
          </Link>
          <Link
            href="/"
            className="rounded-lg border border-hairline px-5 py-2.5 text-sm text-ink-dim transition-colors hover:text-ink"
          >
            Home
          </Link>
        </div>
      </div>
    </main>
  );
}
