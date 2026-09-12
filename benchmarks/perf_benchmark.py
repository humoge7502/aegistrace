"""AegisBench — performance measurement of the ingestion + trust pipeline.

Measures, on a single machine (SQLite, in-process engine — no HTTP):
- event ingestion throughput (batches of 25)
- end-to-end execution wall time (8 events: start, prompt, 4 steps, output, finish)
- compromise-propagation (historical impact) latency over the full graph
- impact-query latency
- database size

Run: python benchmarks/perf_benchmark.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path as _P

sys.path.insert(0, str(_P(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from backend.app.collect.ingest import process_event  # noqa: E402
from backend.app.collect.schemas import EventIn  # noqa: E402
from backend.app.core.crypto import load_or_create_key  # noqa: E402
from backend.app.core.db import make_engine, make_session_factory  # noqa: E402
from backend.app.domain import models  # noqa: E402
from backend.app.domain.enums import FingerprintMode  # noqa: E402
from backend.app.trust import engine as trust  # noqa: E402


def H(n: str) -> str:
    return "sha256:" + hashlib.sha256(str(n).encode()).hexdigest()


AGENT = "perf-agent"
BASE_DOC = {
    "agent_ref": AGENT, "mode": "sequence",
    "steps": [
        {"seq": 1, "kind": "model", "target": "perf-model@1"},
        {"seq": 2, "kind": "retrieval", "target": "kb://perf"},
        {"seq": 3, "kind": "mcp", "target": "mcp://perf-crm"},
        {"seq": 4, "kind": "tool", "target": "tool:send_email"},
    ],
    "component_digests": {"perf-model@1": H("m"), "mcp://perf-crm": H("c"),
                          "tool:send_email": H("t")},
    "prompt_hashes": {},
}


def run(n_executions: int = 200) -> dict:
    tmp = _P(tempfile.mkdtemp(prefix="aegisbench-"))
    engine = make_engine(f"sqlite:///{(tmp / 'perf.db').as_posix()}")
    models.Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    key = load_or_create_key(tmp / "signing.pem")
    with factory() as db:
        t = models.Tenant(name="perf")
        db.add(t)
        db.flush()
        db.add(models.Policy(tenant_id=t.id, name="default", rules={}, is_default=True))
        db.add(models.Baseline(tenant_id=t.id, agent_ref=AGENT, mode=FingerprintMode.SEQUENCE,
                               doc=BASE_DOC))
        db.commit()
        tid = t.id

    def events_for(run_id: str) -> list[EventIn]:
        return [
            EventIn(kind="execution.started", execution_external_id=run_id,
                    payload={"agent_ref": AGENT}),
            EventIn(kind="prompt.pinned", execution_external_id=run_id,
                    payload={"role": "system", "hash": H("sys")}),
            EventIn(kind="step.ended", execution_external_id=run_id,
                    payload={"seq": 1, "kind": "model", "target": "perf-model@1", "digest": H("m")}),
            EventIn(kind="step.ended", execution_external_id=run_id,
                    payload={"seq": 2, "kind": "retrieval", "target": "kb://perf",
                             "meta": {"documents": [{"id": f"d{i}", "hash": H(f"doc{i}")} for i in range(3)]}}),
            EventIn(kind="step.ended", execution_external_id=run_id,
                    payload={"seq": 3, "kind": "mcp", "target": "mcp://perf-crm", "digest": H("c")}),
            EventIn(kind="step.ended", execution_external_id=run_id,
                    payload={"seq": 4, "kind": "tool", "target": "tool:send_email", "digest": H("t")}),
            EventIn(kind="output.produced", execution_external_id=run_id,
                    payload={"digest": H(f"out-{run_id}")}),
            EventIn(kind="execution.finished", execution_external_id=run_id,
                    payload={"execution_external_id": run_id, "status": "completed"}),
        ]

    # warmup
    with factory() as db:
        process_event(db, tid, events_for("warmup")[0], key, "k", "perf")
        db.commit()

    # ingestion throughput: batches of 25 events (8-event executions + padding)
    total_events = 0
    t0 = time.perf_counter()
    exec_times: list[float] = []
    for i in range(n_executions):
        evs = events_for(f"perf-{i}")
        t_exec0 = time.perf_counter()
        with factory() as db:
            for e in evs:
                process_event(db, tid, e, key, "k", "perf")
            db.commit()
        exec_times.append(time.perf_counter() - t_exec0)
        total_events += len(evs)
    ingest_seconds = time.perf_counter() - t0

    # compromise propagation over the whole graph (all executions used mcp://perf-crm)
    t1 = time.perf_counter()
    with factory() as db:
        comp = db.execute(select(models.Component).where(
            models.Component.tenant_id == tid, models.Component.name == "mcp://perf-crm")).scalar_one()
        prop = trust.compromise_component(db, tid, comp, "perf: simulated post-hoc compromise")
        db.commit()
    propagation_seconds = time.perf_counter() - t1

    # impact query
    t2 = time.perf_counter()
    with factory() as db:
        comp = db.execute(select(models.Component).where(
            models.Component.tenant_id == tid, models.Component.name == "mcp://perf-crm")).scalar_one()
        trust.component_impact(db, tid, comp)
    impact_seconds = time.perf_counter() - t2

    db_size = os.path.getsize(tmp / "perf.db")

    result = {
        "benchmark": "AegisBench performance v0",
        "environment": {
            "platform": sys.platform, "database": "sqlite (local file)",
            "mode": "in-process engine (no HTTP)",
        },
        "workload": {
            "executions": n_executions, "events_per_execution": 8,
            "total_events": total_events,
        },
        "results": {
            "ingest_events_per_second": round(total_events / ingest_seconds, 1),
            "ingest_wall_seconds": round(ingest_seconds, 2),
            "execution_avg_ms": round(1000 * sum(exec_times) / len(exec_times), 2),
            "execution_p95_ms": round(1000 * sorted(exec_times)[int(0.95 * len(exec_times)) - 1], 2),
            "compromise_propagation_ms": round(1000 * propagation_seconds, 2),
            "propagation_affected_executions": len(prop["affected_executions"]),
            "propagation_invalidated_outputs": len(prop["affected_outputs"]),
            "propagation_revoked_certificates": len(prop["revoked_certificates"]),
            "impact_query_ms": round(1000 * impact_seconds, 2),
            "db_size_mb": round(db_size / 1e6, 2),
        },
        "note": "Single-machine SQLite numbers; PostgreSQL deployment and HTTP overhead "
                "are expected to differ. Reproducible: python benchmarks/perf_benchmark.py",
    }
    out = _P(__file__).resolve().parents[2] / "docs" / "benchmarks" / "perf-results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
