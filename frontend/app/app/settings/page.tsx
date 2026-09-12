import { apiFetch } from "@/lib/api";
import { Card, EmptyState, JsonEvidence } from "@/components/ui";
import { fmtDate } from "@/lib/trust";
import SettingsClient from "@/components/SettingsClient";

type Policy = { id: string; name: string; rules: Record<string, unknown>; effective_rules?: Record<string, unknown>; is_default: boolean };
type AuditRow = {
  id: string; actor: string; action: string; object_kind: string;
  object_id: string; created_at: string;
};

export default async function SettingsPage() {
  let policies: Policy[] = [];
  let audit: AuditRow[] = [];
  let auditError: string | null = null;
  try {
    [policies, audit] = await Promise.all([
      apiFetch<Policy[]>("/api/v1/policies"),
      apiFetch<AuditRow[]>("/api/v1/audit"),
    ]);
  } catch (e) {
    auditError = (e as { message?: string }).message ?? "load failed";
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-ink-dim">Trust policy rules, API keys and the audit trail.</p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Trust policy (tenant default)">
          {policies.length === 0 ? (
            <p className="text-sm text-ink-faint">No policy rows.</p>
          ) : (
            <ul className="space-y-3">
              {policies.map((p) => (
                <li key={p.id}>
                  <div className="flex items-center gap-2 text-sm font-medium">
                    {p.name}
                    {p.is_default ? <span className="microlabel">default</span> : null}
                  </div>
                  <div className="mt-1"><JsonEvidence data={p.effective_rules ?? p.rules} /></div>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-xs leading-relaxed text-ink-faint">
            Rules map deviation severity → trust state (critical/high → UNTRUSTED,
            medium → DEGRADED, no baseline → UNKNOWN), plus quarantine/certification
            switches. Updates are admin-only and audit-logged.
          </p>
        </Card>

        <Card title="API keys">
          <SettingsClient />
        </Card>

        <Card title="Audit trail (admin)" className="lg:col-span-2">
          {auditError ? (
            <p className="text-sm text-ink-faint">{auditError} (admin role required)</p>
          ) : audit.length === 0 ? (
            <p className="text-sm text-ink-faint">No audit entries yet.</p>
          ) : (
            <ul className="space-y-1.5">
              {audit.slice(0, 12).map((a) => (
                <li key={a.id} className="flex items-center gap-2 rounded border border-hairline bg-surface-2 px-2.5 py-1.5 text-xs">
                  <span className="mono text-ink-dim">{a.action}</span>
                  <span className="text-ink-faint">by {a.actor}</span>
                  <span className="ml-auto text-[10px] text-ink-faint">{fmtDate(a.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
