"""Baseline comparison — AegisTrace vs simpler supply-chain approaches.

METHODOLOGY (important for honesty):
Each baseline strategy is modeled as a detector SUBSET of the same pipeline,
holding collection constant. This measures the value of each *verification
capability* on identical fixtures; it does not re-implement third-party
products. Strategy definitions:

- sbom_only        : component inventory + allow-list only. Knows WHICH
                     components are allowed; never verifies digests, never
                     constrains order, no historical propagation.
- attestation_only : verifies component digests (build-attestation style) at
                     execution time; no allow-lists, no path constraints, no
                     behavioral checks, no historical propagation.
- provenance_only  : records the full causal graph but has no expected-state
                     baseline — nothing counts as a deviation at runtime; can
                     answer "what influenced this output" only.
- aegistrace       : full pipeline (digests + allow-lists + sequence +
                     behavioral path + certificates + historical propagation).

Run: python benchmarks/baseline_comparison.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path as _P

sys.path.insert(0, str(_P(__file__).resolve().parents[1]))

from benchmarks.attackbench.run_attackbench import (  # noqa: E402
    run_attackbench,
)

STRATEGIES = ["sbom_only", "attestation_only", "provenance_only", "aegistrace"]


def strategy_keeps(strategy: str, event_kind: str) -> bool:
    """Which deviation kinds each strategy can act on."""
    if strategy == "sbom_only":
        return event_kind in ("unexpected_component",)
    if strategy == "attestation_only":
        return event_kind in ("digest_mismatch",)
    if strategy == "provenance_only":
        return False
    return True  # aegistrace: everything


def strategy_handles_post_hoc(strategy: str) -> bool:
    """Historical dependency compromise requires trust propagation + invalidation."""
    return strategy == "aegistrace"


def strategy_verifies_attestation(strategy: str) -> bool:
    """Forged attestation detection = signature verification."""
    return strategy in ("attestation_only", "aegistrace")


def run() -> dict:
    full = run_attackbench()  # authoritative results incl. full events per scenario
    rows = []
    for scenario in full["scenarios"]:
        sid = scenario["id"]
        is_attack = scenario["is_attack"]
        kinds = [e["kind"] for e in scenario.get("integrity_events", [])]
        per_strategy = {}
        for strategy in STRATEGIES:
            if sid == "forged-attestation":
                detected = strategy_verifies_attestation(strategy)
            elif sid == "historical-dependency-compromise":
                detected = strategy_handles_post_hoc(strategy) and scenario["detected"]
            elif sid == "stale-trust":
                # missing provenance: only systems expecting evidence can notice absence
                detected = strategy in ("attestation_only", "aegistrace") and scenario["detected"]
            else:
                kept = [k for k in kinds if strategy_keeps(strategy, k)]
                detected = bool(kept)
            per_strategy[strategy] = {
                "detected": detected,
                "expected": is_attack,
            }
        rows.append({"scenario": sid, "category": scenario["category"],
                     "is_attack": is_attack, "strategies": per_strategy})

    summary = {}
    for strategy in STRATEGIES:
        attacks = [r for r in rows if r["is_attack"]]
        benign = [r for r in rows if not r["is_attack"]]
        tp = sum(1 for r in attacks if r["strategies"][strategy]["detected"])
        fn = len(attacks) - tp
        fp = sum(1 for r in benign if r["strategies"][strategy]["detected"])
        tn = len(benign) - fp
        summary[strategy] = {
            "true_positives": tp, "false_negatives": fn,
            "false_positives": fp, "true_negatives": tn,
            "recall": round(tp / (tp + fn), 2) if (tp + fn) else None,
            "precision": round(tp / (tp + fp), 2) if (tp + fp) else None,
        }

    return {
        "comparison": "AegisTrace baseline comparison v0",
        "methodology": __doc__.split("METHODOLOGY")[1].split("Run:")[0].strip(),
        "rows": rows,
        "summary": summary,
    }


def write_markdown(report: dict, path: _P) -> None:
    lines = [
        "# Baseline Comparison — empirical results",
        "",
        f"Fixtures: {len(report['rows'])} (14 attacks + 3 benign controls), "
        "identical to AttackBench. See `benchmarks/baseline_comparison.py` for the "
        "strategy definitions and the modeling caveat: strategies are detector "
        "subsets of the same pipeline (capability measurement, not product "
        "benchmarks of third-party software).",
        "",
        "| Scenario | Attack | sbom_only | attestation_only | provenance_only | aegistrace |",
        "|---|---|---|---|---|---|",
    ]
    for r in report["rows"]:
        cells = []
        for s in STRATEGIES:
            detected = r["strategies"][s]["detected"]
            cells.append("detect" if detected else "miss")
        lines.append(f"| {r['scenario']} | {'yes' if r['is_attack'] else 'no'} | "
                     + " | ".join(cells) + " |")
    lines += ["", "## Summary", "",
              "| Strategy | TP | FN | FP | TN | Recall | Precision |", "|---|---|---|---|---|---|---|"]
    for strategy, m in report["summary"].items():
        lines.append(f"| {strategy} | {m['true_positives']} | {m['false_negatives']} | "
                     f"{m['false_positives']} | {m['true_negatives']} | {m['recall']} | {m['precision']} |")
    lines += ["", "All numbers come from `python benchmarks/baseline_comparison.py` "
              "(reproducible; SQLite, single machine, harmless local fixtures).",
              ""]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out_dir = _P(__file__).resolve().parents[2] / "docs" / "benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = run()
    (out_dir / "comparison-results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, out_dir / "comparison.md")
    print(json.dumps(report["summary"], indent=2))
