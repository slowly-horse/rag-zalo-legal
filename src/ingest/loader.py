"""Read the local BEIR-style JSONL files.

This module deliberately knows nothing about application settings or how the
files were downloaded. Callers pass a :class:`pathlib.Path`, which keeps the
loader easy to reuse and easy to test.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from src.schemas import CorpusRecord, QrelSet, Query

JsonObject = dict[str, Any]


def read_jsonl(path: Path) -> Iterator[JsonObject]:
    """Yield one JSON object per non-empty line.

    Invalid JSON is reported with its file and line number instead of being
    silently skipped.
    """
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON at {path}:{line_number}") from error

            if not isinstance(row, dict):
                raise ValueError(f"Expected a JSON object at {path}:{line_number}")

            yield row


def _identifier(row: JsonObject) -> str | None:
    """Read the BEIR ``_id`` key, while also accepting the parquet ``id`` key."""
    value = row.get("_id") or row.get("id")
    return str(value) if value is not None else None


def iter_corpus(path: Path, limit: int | None = None) -> Iterator[CorpusRecord]:
    """Stream corpus records without loading the whole file into memory."""
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to 0")

    emitted = 0
    for row in read_jsonl(path):
        if limit is not None and emitted >= limit:
            return

        doc_id = _identifier(row)
        if doc_id is None:
            raise ValueError(f"Corpus row is missing `_id`: {row!r}")

        yield CorpusRecord(
            doc_id=doc_id,
            title=row.get("title") or "",
            text=row.get("text") or "",
        )
        emitted += 1


def load_queries(path: Path) -> tuple[dict[str, Query], int]:
    """Load unique queries by id and return how many duplicate rows were dropped."""
    queries: dict[str, Query] = {}
    duplicates = 0

    for row in read_jsonl(path):
        query_id = _identifier(row)
        if query_id is None:
            raise ValueError(f"Query row is missing `_id`: {row!r}")

        if query_id in queries:
            duplicates += 1
            continue

        queries[query_id] = Query(
            query_id=query_id,
            text=row.get("text") or "",
        )

    return queries, duplicates


def load_qrels(path: Path, *, name: str) -> QrelSet:
    """Load qrels as ``query_id -> {doc_id: relevance_score}``."""
    qrels = QrelSet(name=name)

    for row in read_jsonl(path):
        query_id = row.get("query-id")
        doc_id = row.get("corpus-id")

        if query_id is None or doc_id is None:
            raise ValueError(
                "Qrel row must contain `query-id` and `corpus-id`: "
                f"{row!r}"
            )

        score = int(float(row.get("score", 1)))
        qrels.labels.setdefault(str(query_id), {})[str(doc_id)] = score

    return qrels
