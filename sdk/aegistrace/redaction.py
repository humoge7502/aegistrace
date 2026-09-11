"""Redaction helpers — hash-by-default content handling (ADR-005)."""

from __future__ import annotations

import hashlib
import json


def hash_content(content: object) -> str:
    if isinstance(content, str):
        data = content.encode("utf-8")
    elif isinstance(content, (dict, list)):
        data = json.dumps(content, sort_keys=True, ensure_ascii=False).encode("utf-8")
    else:
        data = str(content).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def document_refs(documents: list) -> list[dict]:
    """Convert retrieved documents to minimal references (id + hash)."""
    refs = []
    for i, doc in enumerate(documents):
        if isinstance(doc, dict):
            refs.append({
                "id": str(doc.get("id", f"doc-{i}")),
                "hash": hash_content(doc.get("text", doc.get("content", ""))),
            })
        else:
            refs.append({"id": f"doc-{i}", "hash": hash_content(doc)})
    return refs
