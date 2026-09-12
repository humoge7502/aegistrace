# Benchmark Methodology

_All results in `docs/benchmarks/` are reproducible from the repository with a
single command on a plain machine. No number in this project is quoted without
a generating script._

## AttackBench (`benchmarks/attackbench/run_attackbench.py`)

- **Fixtures**: 14 attack scenarios + 3 benign controls (17 total). All attacks
  are harmless local simulations: "tampering" = emitting events whose observed
  digests differ from the pinned baseline; no real-world exploitation tooling.
- **Fresh state**: every scenario runs in its own in-process engine + SQLite DB
  (no cross-scenario contamination).
- **Detection contract**: a run is "detected" when it is NOT left TRUSTED —
  an integrity event fired, the certificate was rejected, or the output was
  invalidated. For benign controls, flagged = false positive. Missing evidence
  (stale-trust) counting as detected reflects the UNKNOWN ≠ TRUSTED doctrine.
- **Metrics**: TP/FP/FN/TN, precision, recall, accuracy over the 17 fixtures.
- **Current result** (this machine, 2026-09-12): precision 1.0, recall 1.0,
  accuracy 1.0 (`attackbench-results.json`).

## Baseline comparison (`benchmarks/baseline_comparison.py`)

- **Modeling caveat (important)**: strategies are modeled as detector SUBSETS of
  the same pipeline, holding collection constant. This measures the marginal
  value of each *verification capability* on identical fixtures; it is not a
  benchmark of third-party products.
  - `sbom_only`: allow-list only (no digests, no path, no propagation)
  - `attestation_only`: digest verification + signature verification
  - `provenance_only`: full graph recording, no expected-state comparison
  - `aegistrace`: everything
- **Current result**: recall sbom_only 0.36, attestation_only 0.64,
  provenance_only 0.0, aegistrace 1.0 (`comparison.md`).

## Performance (AegisBench, `benchmarks/perf_benchmark.py`)

- Workload: 200 executions × 8 events, in-process engine, SQLite.
- Measures: ingest throughput, per-execution wall time (avg/p95), compromise
  propagation latency over the full graph, impact-query latency, DB size.
- **Current result**: 117 events/s; execution avg 68 ms; propagation over 200
  executions 871 ms (200 outputs invalidated, 200 certs revoked); impact query
  471 ms (`perf-results.json`).
- Honest caveats: single machine, SQLite, no HTTP overhead, no concurrency.
  Numbers establish order-of-magnitude feasibility, not production capacity.

## Threats to validity

1. Attack fixtures and detector strategies were authored by the same project —
   independence requires external review (documented as future work).
2. The benign-control set is small (3); false-positive rate estimates need
   realistic production trace corpora.
3. Performance numbers vary by hardware; regenerate on target hardware.
