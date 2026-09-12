import { readFile } from "node:fs/promises";
import path from "node:path";

import { Card, EmptyState } from "@/components/ui";

type AttackBenchReport = {
  benchmark: string;
  note: string;
  metrics: {
    attacks: number; true_positives: number; false_negatives: number;
    benign_controls: number; false_positives: number; true_negatives: number;
    precision: number | null; recall: number | null; accuracy: number | null;
  };
  scenarios: {
    id: string; category: string; is_attack: boolean; detected: boolean;
    trust_state: string; extras: Record<string, unknown>;
  }[];
};

export default async function AttackBenchPage() {
  let report: AttackBenchReport | null = null;
  try {
    const p = path.join(process.cwd(), "..", "docs", "benchmarks", "attackbench-results.json");
    report = JSON.parse(await readFile(p, "utf-8")) as AttackBenchReport;
  } catch {
    report = null;
  }

  if (!report) {
    return (
      <EmptyState
        title="AttackBench results not found"
        hint="Generate them with: python benchmarks/attackbench/run_attackbench.py (writes docs/benchmarks/attackbench-results.json)."
      />
    );
  }

  const m = report.metrics;
  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">AttackBench</h1>
        <p className="mt-1 max-w-3xl text-sm text-ink-dim">{report.note}</p>
      </header>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        <Stat label="Attacks" value={m.attacks} />
        <Stat label="Detected (TP)" value={m.true_positives} tone="text-trust" />
        <Stat label="Missed (FN)" value={m.false_negatives} tone="text-untrust" />
        <Stat label="False alarms (FP)" value={m.false_positives} tone="text-degraded" />
        <Stat label="Recall / Precision" value={`${m.recall ?? "—"} / ${m.precision ?? "—"}`} tone="text-accent" />
      </div>

      <Card title="Scenario results">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-hairline text-left">
                <th className="microlabel px-3 py-2">Scenario</th>
                <th className="microlabel px-3 py-2">Category</th>
                <th className="microlabel px-3 py-2">Type</th>
                <th className="microlabel px-3 py-2">Outcome</th>
                <th className="microlabel px-3 py-2">Final state</th>
              </tr>
            </thead>
            <tbody>
              {report.scenarios.map((s) => (
                <tr key={s.id} className="border-b border-hairline/50 last:border-0">
                  <td className="mono px-3 py-2">{s.id}</td>
                  <td className="px-3 py-2 text-xs text-ink-dim">{s.category}</td>
                  <td className="px-3 py-2 text-xs text-ink-faint">{s.is_attack ? "attack" : "benign control"}</td>
                  <td className="px-3 py-2">
                    {s.is_attack ? (
                      s.detected
                        ? <span className="text-trust">detected</span>
                        : <span className="text-untrust">missed</span>
                    ) : (
                      s.detected
                        ? <span className="text-degraded">false positive</span>
                        : <span className="text-trust">correctly passed</span>
                    )}
                  </td>
                  <td className="mono px-3 py-2 text-xs uppercase text-ink-dim">{s.trust_state}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number | string; tone?: string }) {
  return (
    <div className="rounded-[10px] border border-hairline bg-surface px-4 py-3">
      <div className="microlabel">{label}</div>
      <div className={`mono mt-1 text-2xl font-semibold ${tone ?? "text-ink"}`}>{value}</div>
    </div>
  );
}
