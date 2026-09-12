import Link from "next/link";
import { notFound } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { Card, SeverityBadge, TrustBadge } from "@/components/ui";
import { fmtDate, shortDigest } from "@/lib/trust";
import CertificateCard from "@/components/CertificateCard";
import GraphViewer, { type GraphEdge, type GraphNode } from "@/components/GraphViewer";

type Passport = {
  passport_version: string;
  execution: {
    id: string; external_id: string; agent_ref: string; agent_version: string | null;
    status: string; trust_state: string; fingerprint: string | null;
    started_at: string; finished_at: string | null;
  };
  prompt_hashes: Record<string, string>;
  components: { kind: string; target: string; digest: string | null; seq: number;
    trust_state: string; digest_expected: string | null; digest_observed: string | null }[];
  outputs: { id: string; external_id: string; digest: string; trust_state: string; quarantined: boolean }[];
  trust: {
    state: string;
    decisions: { state: string; reason: string; evidence: Record<string, unknown>; decided_by: string; created_at: string }[];
    integrity_events: { id: string; kind: string; severity: string; title: string;
      expected: Record<string, unknown> | null; observed: Record<string, unknown> | null; created_at: string }[];
  };
  certificate: { serial: string; status: string; signature: string; statement: Record<string, unknown>; issued_at: string } | null;
};

type Graph = { nodes: GraphNode[]; edges: GraphEdge[] };

export default async function ExecutionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let passport: Passport;
  let graph: Graph;
  try {
    [passport, graph] = await Promise.all([
      apiFetch<Passport>(`/api/v1/executions/${id}/passport`),
      apiFetch<Graph>(`/api/v1/executions/${id}/graph`),
    ]);
  } catch (e) {
    const status = (e as { status?: number }).status;
    if (status === 404) notFound();
    return (
      <Card title="Error">
        <p className="text-sm text-ink-dim">{(e as { message?: string }).message}</p>
      </Card>
    );
  }

  const ex = passport.execution;
  const hasDeviation = passport.trust.integrity_events.length > 0;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="mono text-lg font-bold">{ex.external_id}</h1>
            <TrustBadge state={ex.trust_state} />
          </div>
          <p className="mt-1 text-sm text-ink-dim">
            {ex.agent_ref}{ex.agent_version ? ` @${ex.agent_version}` : ""} · {ex.status} ·{" "}
            {fmtDate(ex.started_at)} → {fmtDate(ex.finished_at)}
          </p>
        </div>
        <Link href="/app/executions" className="text-sm text-ink-dim hover:text-ink">← all executions</Link>
      </header>

      {hasDeviation ? (
        <div className="rounded-[10px] border border-untrust/40 bg-untrust/5 p-4">
          <div className="microlabel text-untrust">what happened · why</div>
          <ul className="mt-2 space-y-2">
            {passport.trust.integrity_events.map((e) => (
              <li key={e.id} className="text-sm">
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={e.severity} />
                  <span className="mono text-xs text-ink-faint">{e.kind}</span>
                  <span className="ml-auto text-[10px] text-ink-faint">{fmtDate(e.created_at)}</span>
                </div>
                <div className="mt-0.5 font-medium">{e.title}</div>
                <div className="mt-1 grid gap-2 text-xs text-ink-dim sm:grid-cols-2">
                  {e.expected ? <pre className="mono overflow-x-auto whitespace-pre-wrap break-all rounded border border-hairline bg-canvas p-2">{JSON.stringify(e.expected)}</pre> : null}
                  {e.observed ? <pre className="mono overflow-x-auto whitespace-pre-wrap break-all rounded border border-hairline bg-canvas p-2">{JSON.stringify(e.observed)}</pre> : null}
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-5">
        <div className="space-y-4 xl:col-span-3">
          <Card title="Causal trust graph">
            <GraphViewer nodes={graph.nodes} edges={graph.edges} />
          </Card>

          <Card title="Execution steps (observed)">
            <ol className="space-y-1.5">
              {passport.components.map((c, i) => (
                <li key={i} className="flex items-center gap-3 rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                  <span className="mono w-6 text-center text-xs text-ink-faint">{c.seq}</span>
                  <span className="rounded bg-canvas px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-ink-dim">{c.kind}</span>
                  <span className="mono truncate text-sm">{c.target}</span>
                  <span className="mono ml-auto hidden text-[10px] text-ink-faint sm:block">{shortDigest(c.digest)}</span>
                  <TrustBadge state={c.trust_state} small />
                </li>
              ))}
              {passport.components.length === 0 ? (
                <li className="text-sm text-ink-faint">No steps recorded — provenance missing.</li>
              ) : null}
            </ol>
          </Card>
        </div>

        <div className="space-y-4 xl:col-span-2">
          <CertificateCard
            serial={passport.certificate?.serial ?? null}
            status={passport.certificate?.status ?? null}
            issuedAt={passport.certificate?.issued_at ?? null}
            statement={passport.certificate?.statement ?? null}
          />

          <Card title="Outputs">
            {passport.outputs.length === 0 ? (
              <p className="text-sm text-ink-faint">No outputs produced.</p>
            ) : (
              <ul className="space-y-2">
                {passport.outputs.map((o) => (
                  <li key={o.id} className="rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                    <div className="flex items-center justify-between">
                      <span className="mono text-xs">{o.external_id}</span>
                      <TrustBadge state={o.trust_state} small />
                    </div>
                    <div className="mono mt-1 break-all text-[10px] text-ink-faint">{o.digest}</div>
                    {o.quarantined ? (
                      <div className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-quarantined">
                        quarantined — blocked from downstream use
                      </div>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Trust decisions (evidence chain)">
            <ul className="space-y-2">
              {passport.trust.decisions.map((d, i) => (
                <li key={i} className="rounded-lg border border-hairline bg-surface-2 px-3 py-2">
                  <div className="flex items-center justify-between">
                    <TrustBadge state={d.state} small />
                    <span className="text-[10px] text-ink-faint">{fmtDate(d.created_at)}</span>
                  </div>
                  <p className="mt-1 text-xs leading-relaxed text-ink-dim">{d.reason}</p>
                  <p className="mt-1 text-[10px] text-ink-faint">decided by {d.decided_by}</p>
                </li>
              ))}
            </ul>
          </Card>

          <Card title="Pinned prompts">
            {Object.entries(passport.prompt_hashes).length === 0 ? (
              <p className="text-sm text-ink-faint">None pinned.</p>
            ) : (
              <ul className="space-y-1">
                {Object.entries(passport.prompt_hashes).map(([role, hash]) => (
                  <li key={role} className="flex items-center justify-between text-xs">
                    <span className="text-ink-dim">{role}</span>
                    <span className="mono text-ink-faint">{shortDigest(hash)}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Execution fingerprint">
            <p className="mono break-all text-xs text-ink-dim">{ex.fingerprint ?? "—"}</p>
            <p className="mt-2 text-[11px] leading-relaxed text-ink-faint">
              sha256 over the canonical ordered step signatures — the certificate subject.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
