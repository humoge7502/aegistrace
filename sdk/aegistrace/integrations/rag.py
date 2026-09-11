"""RAG integration — record retrieval events with document references."""

from __future__ import annotations

from aegistrace.context import current_run
from aegistrace.redaction import document_refs


def record_retrieval(index_id: str, documents: list, embedding_model: str | None = None) -> list[dict]:
    """Record a retrieval step against a vector index. Documents are reduced to
    (id, sha256) references; raw text never leaves the process by default."""
    run = current_run()
    if run is None or run.finished:
        return []
    meta: dict = {"documents": document_refs(documents), "document_count": len(documents)}
    if embedding_model:
        meta["embedding_model"] = embedding_model
    run.record_step("retrieval", index_id, meta=meta)
    return meta["documents"]
