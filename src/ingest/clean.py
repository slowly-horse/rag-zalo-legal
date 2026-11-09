from src.schemas import CorpusRecord
import unicodedata


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # NFC keeps Vietnamese tone marks in a single canonical form. Without this,
    # visually identical words tokenise differently and BM25 (T2) silently misses matches.
    out = unicodedata.normalize("NFC", text)
    out = out.replace("\u00a0", " ")
    out = out.replace("\r\n", "\n").replace("\r", "\n")
    return out.strip()


def normalize_record(record: CorpusRecord) -> CorpusRecord:
    return CorpusRecord(
        doc_id=record.doc_id,
        title=normalize_text(record.title),
        text=normalize_text(record.text),
    )