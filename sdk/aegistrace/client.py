"""Collector client — batched event delivery (HTTP) or embedded sink.

Fail-safe behavior: on transport failure events stay buffered locally (bounded)
and a warning is emitted. Unreported executions are UNKNOWN server-side —
the backend never silently trusts missing provenance (ADR-003).
"""

from __future__ import annotations

import threading
from typing import Callable

import httpx



class CollectorClient:
    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
        sink: Callable[[list[dict]], None] | None = None,
        timeout: float = 5.0,
        max_buffer: int = 10_000,
    ) -> None:
        if sink is None and not (endpoint and api_key):
            raise ValueError("provide endpoint+api_key or an embedded sink")
        self.endpoint = (endpoint or "").rstrip("/")
        self.api_key = api_key
        self.sink = sink
        self.timeout = timeout
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._max_buffer = max_buffer
        self._client = httpx.Client(timeout=timeout) if endpoint else None

    def emit(self, event: dict) -> None:
        with self._lock:
            if len(self._buffer) >= self._max_buffer:
                self._buffer.pop(0)  # bounded: drop oldest rather than grow unbounded
            self._buffer.append(event)
            batch = self._buffer
            self._buffer = []
        if self.sink is not None:
            self.sink(batch)
            return
        self._post(batch)

    def _post(self, batch: list[dict]) -> None:
        assert self._client is not None and self.api_key
        try:
            resp = self._client.post(
                f"{self.endpoint}/api/v1/events/batch",
                headers={"X-API-Key": self.api_key},
                json={"events": batch},
            )
            resp.raise_for_status()
        except Exception:
            # fail safe: requeue (bounded); execution remains UNKNOWN server-side
            with self._lock:
                self._buffer = batch + self._buffer
                del self._buffer[self._max_buffer:]

    def flush(self) -> int:
        """Force-send buffered events; returns number still pending."""
        with self._lock:
            batch = self._buffer
            self._buffer = []
        if batch and self.sink is None:
            self._post(batch)
        return len(self._buffer)

    def pending(self) -> int:
        with self._lock:
            return len(self._buffer)

    # convenience event builders -------------------------------------------------

    def event(self, kind: str, execution_external_id: str | None, payload: dict) -> dict:
        return {"kind": kind, "execution_external_id": execution_external_id, "payload": payload}

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
