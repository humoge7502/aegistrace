# Contributing

## Setup

```bash
python -m venv .venv && source .venv/Scripts/activate
pip install -e ./backend -e ./sdk pytest pytest-timeout ruff mypy
cd frontend && npm install
```

## Quality gates (all must pass before merge)

```bash
pytest backend/tests -q                                   # 35 tests
python benchmarks/attackbench/run_attackbench.py          # recall must stay 1.0
ruff check backend/app sdk benchmarks demo --select E9,F63,F7,F82,F401 --ignore E402
cd frontend && npm run build                              # type check + build
```

CI (`.github/workflows/ci.yml`) runs the same gates on push/PR.

## Ground rules

1. **Unknown ≠ TRUSTED** — never weaken a default that converts missing
   evidence into trust. If a test asserts TRUSTED, evidence must exist.
2. **No weakened tests** — failing behavior means fix the code, not the assert.
3. **Explainability** — every trust-state change must produce a TrustDecision
   with an evidence chain a reviewer can read.
4. **Privacy** — content stays hashed by default; new collectors must redact
   (ADR-005).
5. **New attack surface** → new AttackBench fixture + threat-model entry.
6. Read `docs/agent-state/PROJECT-STATE.md` before starting; update it and
   `docs/tasks/TASK-BOARD.md` after meaningful changes.

## Project layout

See the repository README table. Backend conventions: SQLAlchemy 2.0 typed
mappings, Pydantic v2 schemas at the boundary, JSON columns reassigned (never
mutated in place), per-event flush in ingestion, tenant scoping in every query.
