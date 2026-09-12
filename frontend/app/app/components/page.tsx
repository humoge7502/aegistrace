import { apiFetch } from "@/lib/api";
import { Card, EmptyState, TrustBadge } from "@/components/ui";
import { fmtDate } from "@/lib/trust";
import ComponentsClient from "@/components/ComponentsClient";

type ComponentRow = {
  id: string; kind: string; name: string; version: string | null;
  digest_expected: string | null; digest_observed: string | null;
  trust_state: string; state_reason: string | null; state_updated_at: string;
};

export default async function ComponentsPage() {
  let rows: ComponentRow[];
  try {
    rows = await apiFetch<ComponentRow[]>("/api/v1/components");
  } catch (e) {
    return <EmptyState title="Could not load components" hint={(e as { message?: string }).message} />;
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">Components</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Provenance entities with expected/observed digests and live trust states.
          Marking a component COMPROMISED propagates through every execution that used it.
        </p>
      </header>
      <ComponentsClient rows={rows} />
    </div>
  );
}
