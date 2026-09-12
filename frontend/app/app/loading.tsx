import { SkeletonBlock, SkeletonRow } from "@/components/Skeleton";

export default function AppLoading() {
  return (
    <div className="space-y-5" role="status" aria-label="Loading console">
      <div>
        <SkeletonBlock className="h-6 w-44" />
        <SkeletonBlock className="mt-2 h-4 w-72" />
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-[10px] border border-hairline bg-surface px-4 py-3">
            <SkeletonBlock className="h-2.5 w-20" />
            <SkeletonBlock className="mt-3 h-7 w-14" />
          </div>
        ))}
      </div>
      <div className="rounded-[10px] border border-hairline bg-surface p-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
      <span className="sr-only">Loading, please wait.</span>
    </div>
  );
}
