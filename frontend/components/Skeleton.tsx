export function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded bg-surface-2 ${className}`}
      aria-hidden="true"
    />
  );
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 border-b border-hairline/60 py-3 last:border-0">
      <SkeletonBlock className="h-3.5 w-28" />
      <SkeletonBlock className="h-3.5 flex-1 max-w-40" />
      <SkeletonBlock className="ml-auto h-5 w-20 rounded-full" />
    </div>
  );
}
