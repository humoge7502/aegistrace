"""Minimal in-process metrics (Prometheus text exposition).

Single-instance counters — sufficient for local runs and tests; production
deployments can export via OpenTelemetry (optional extra).
"""

from __future__ import annotations

import threading


class Metrics:
    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._lock = threading.Lock()

    def bump(self, name: str, by: float = 1.0) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0.0) + by

    def render(self) -> str:
        with self._lock:
            lines = []
            for name in sorted(self._counters):
                value = self._counters[name]
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
            return "\n".join(lines) + "\n"
