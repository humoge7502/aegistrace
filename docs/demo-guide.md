# Demo Guide — the killer demo

`python demo/killer_demo.py` (from the repo root, backend deps installed).

The script starts its own server on 127.0.0.1:8420 with a throwaway database,
or attaches to an already-running one with `AEGISTRACE_DEMO_EXTERNAL=1`.
Everything is local and harmless — the model, CRM and MCP server are simulated
fixtures. **All output is DEMO DATA.**

## The five phases

| Phase | Action | Result |
|---|---|---|
| 1 | Agent runs the expected path (model → retrieval → MCP → email tool) | `TRUSTED` + certificate `ATC-…`, verification passes |
| 2 | MCP fixture payload tampered (digest `bb…` → `cc…`), output unchanged | `digest_mismatch` (critical) → execution `UNTRUSTED`, no certificate |
| 3 | Extra "external-attacker" MCP call inserted mid-run; final output still normal | `unexpected_component` + `path_deviation` → `UNTRUSTED` — *the path betrayed it* |
| 4 | MCP component declared COMPROMISED after the fact | incident created; **all 3 past executions invalidated**, 3 outputs quarantined, phase-1 certificate REVOKED |
| 5 | Fixture restored to trusted digest, agent re-runs marked `rerun_of` | `RE-CERTIFIED` + fresh ACTIVE certificate |

Machine-readable report: `demo/report.json`.

## What this demonstrates (the thesis)

1. Machine-readable provenance for every influencing component.
2. Expected-vs-observed verification (digests, allow-lists, path, prompts).
3. Behavioral/execution-path deviation caught even with a normal-looking output.
4. Explainable trust propagation with per-hop evidence chains.
5. Output dependency tracing + invalidation (historical, not just future).
6. Quarantine, recovery, and re-certification semantics.

## Verify it yourself

```bash
# after the demo, inspect the invalidated run + revoked certificate:
curl -s localhost:8420/api/v1/executions \
  -H "X-API-Key: <bootstrap key>" | python -m json.tool
```
