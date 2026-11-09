"""Shared data contracts.

Kept as one module rather than a package: these are the few structures that
cross package boundaries (ingest -> index -> retrieve -> eval).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LegalMetadata(BaseModel):
    """Parsed from a corpus id like ``01/2009/tt-bnn+1`` plus its title.

    These fields become the metadata filters of T5 (document type, year,
    issuer), so they are extracted from day one even though nothing filters yet.
    """

    doc_key: str = Field(description="Document identifier, e.g. 01/2009/tt-bnn")
    doc_number: str | None = None
    year: int | None = None
    doc_code: str | None = Field(default=None, description="Raw code, e.g. tt-bnn, qh14")
    doc_type: str | None = Field(default=None, description="Normalised type, e.g. thong_tu")
    doc_type_label: str | None = None
    issuer: str | None = Field(default=None, description="Issuing body code, e.g. cp, btc")
    article_index: int | None = Field(default=None, description="Index within the document")
    article_no: str | None = Field(default=None, description="Điều number from the title")
    article_heading: str | None = None
    khoan_no: str | None = Field(default=None, description="Khoản number when sub-chunked")
    parse_ok: bool = True


class CorpusRecord(BaseModel):
    """One document loaded from ``corpus.jsonl``.

    The loader renames the raw ``_id`` field to ``doc_id``::

        CorpusRecord(
            doc_id="01/2009/tt-bnn+1",
            title="Điều 1. Phạm vi áp dụng",
            text="Thông tư này hướng dẫn...",
        )
    """

    doc_id: str = Field(description="Value of the raw corpus `_id` field")
    title: str = ""
    text: str = ""


class Passage(BaseModel):
    """One indexable unit of text."""

    passage_id: str = Field(description="Unique per chunk; equals doc_id for article chunks")
    doc_id: str = Field(description="Corpus id — the unit golden labels refer to")
    title: str
    text: str
    embed_text: str = Field(description="Exactly what gets embedded (title + text)")
    n_chars: int
    metadata: LegalMetadata


class Query(BaseModel):
    """One search question loaded from ``queries.jsonl``.

    Example::

        Query(
            query_id="0637bf82c8b290c7875c5bfddbf91df5",
            text="Công an xã xử phạt lỗi không mang bằng lái xe có đúng không?",
        )
    """

    query_id: str
    text: str


class QrelSet(BaseModel):
    """Relevance labels grouped as ``query_id -> {doc_id: score}``.

    One query may have more than one relevant document::

        QrelSet(
            name="train",
            labels={
                "query-1": {
                    "document-1": 1,
                    "document-2": 1,
                }
            },
        )
    """

    name: str
    labels: dict[str, dict[str, int]] = Field(default_factory=dict)

    @property
    def n_labels(self) -> int:
        return sum(len(documents) for documents in self.labels.values())

    @property
    def query_ids(self) -> set[str]:
        return set(self.labels)


class GoldenExample(BaseModel):
    """A query with its relevant document ids."""

    query_id: str
    text: str
    relevant_doc_ids: list[str]
    # Graded relevance is kept even though this dataset is binary (all scores
    # are 1), so nDCG stays meaningful if graded labels are added later.
    scores: dict[str, int] = Field(default_factory=dict)


class SplitStats(BaseModel):
    name: str
    n_queries: int
    n_labels: int
    mean_labels_per_query: float
    multi_label_queries: int
    excluded_overlap: int = 0
