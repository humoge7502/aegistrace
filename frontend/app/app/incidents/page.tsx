import { apiFetch } from "@/lib/api";
import { EmptyState } from "@/components/ui";
import IncidentsClient from "@/components/IncidentsClient";

type Incident = {
  id: string; title: string; severity: string; status: string;
  description: string; evidence: Record<string, unknown>;
  created_at: string;
};

export default async function IncidentsPage() {
  let rows: Incident[];
  try {
    rows = await apiFetch<Incident[]>("/api/v1/incidents");
  } catch (e) {
    return <EmptyState title="Could not load incidents" hint={(e as { message?: string }).message} />;
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">Incidents</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Compromise events with their full propagation evidence. Actions: contain →
          recover (restore trusted digest) → resolve.
        </p>
      </header>
      {rows.length === 0 ? (
        <EmptyState title="No incidents" hint="When a component is compromised, an incident is opened with the complete affected list." />
      ) : (
        <IncidentsClient rows={rows} />
      )}
    </div>
  );
}
