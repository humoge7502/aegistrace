# Baseline Comparison — empirical results

Fixtures: 17 (14 attacks + 3 benign controls), identical to AttackBench. See `benchmarks/baseline_comparison.py` for the strategy definitions and the modeling caveat: strategies are detector subsets of the same pipeline (capability measurement, not product benchmarks of third-party software).

| Scenario | Attack | sbom_only | attestation_only | provenance_only | aegistrace |
|---|---|---|---|---|---|
| model-tampering | yes | miss | detect | miss | detect |
| prompt-tampering | yes | miss | miss | miss | detect |
| dataset-poisoning | yes | miss | detect | miss | detect |
| dependency-substitution | yes | detect | detect | miss | detect |
| container-modification | yes | detect | detect | miss | detect |
| rag-poisoning | yes | detect | miss | miss | detect |
| tool-compromise | yes | miss | detect | miss | detect |
| mcp-compromise | yes | miss | detect | miss | detect |
| runtime-manipulation | yes | detect | miss | miss | detect |
| path-deviation | yes | detect | miss | miss | detect |
| multi-component | yes | miss | detect | miss | detect |
| forged-attestation | yes | miss | detect | miss | detect |
| stale-trust | yes | miss | detect | miss | detect |
| historical-dependency-compromise | yes | miss | miss | miss | detect |
| benign-exact | no | miss | miss | miss | miss |
| benign-meta-variation | no | miss | miss | miss | miss |
| benign-recovery-flow | no | miss | miss | miss | miss |

## Summary

| Strategy | TP | FN | FP | TN | Recall | Precision |
|---|---|---|---|---|---|---|
| sbom_only | 5 | 9 | 0 | 3 | 0.36 | 1.0 |
| attestation_only | 9 | 5 | 0 | 3 | 0.64 | 1.0 |
| provenance_only | 0 | 14 | 0 | 3 | 0.0 | None |
| aegistrace | 14 | 0 | 0 | 3 | 1.0 | 1.0 |

All numbers come from `python benchmarks/baseline_comparison.py` (reproducible; SQLite, single machine, harmless local fixtures).
