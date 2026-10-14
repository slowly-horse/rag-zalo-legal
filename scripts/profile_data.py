import json
from pathlib import Path
from collections import defaultdict
import random


def read_jsonl(path: str):
    with Path(path).open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                print(f"JSON lỗi tại {path}:{line_number}: {error}")

def percentile(values: list[int], ratio: float) -> int:
    ordered = sorted(values)
    index = round((len(ordered) -1) * ratio)
    return ordered[index]

def profile_corpus() -> None:
    lengths = []
    empty_documents = []
    for row in read_jsonl("data/raw/corpus.jsonl"):
        text = row.get("text", "")
        lengths.append(len(text))

        if not text.strip():
            empty_documents.append(row.get("_id"))
            
    print("CORPUS")
    print("Số lượng văn bản:", len(lengths))
    print("Số lượng văn bản rỗng:", len(empty_documents))
    print("Ví dụ ID có văn bản rỗng:", empty_documents[:5])
    print("Độ dài nhỏ nhất:", min(lengths))
    print("Độ dài lớn nhất:", max(lengths))
    print("Độ dài trung bình:", sum(lengths) / len(lengths))
    print("Độ dài phần trăm 50 - p50:", percentile(lengths, 0.50))
    print("Độ dài phần trăm 90 - p90:", percentile(lengths, 0.90))
    print("Độ dài phần trăm 99 - p99:", percentile(lengths, 0.99))

def profile_qrels(split: str) -> None:
    path = f"data/raw/qrels/{split}.jsonl"

    documents_by_query: dict[str, set[str]] = defaultdict(set)

    for row in read_jsonl(path):
        query_id = row["query-id"]
        corpus_id = row["corpus-id"]

        documents_by_query[query_id].add(corpus_id)

    multi_document_queries = {
        query_id: document_ids
        for query_id, document_ids in documents_by_query.items() if len(document_ids) > 1
    }

    print(f"\nQRELS {split.upper()}")
    print("Số query:", len(documents_by_query))
    print("Query có nhiều hơn 1 document:", len(multi_document_queries))

    for query_id, document_ids in list(multi_document_queries.items())[:5]:
        print(query_id, "->" , sorted(document_ids))


def inspect_empty_bodies(sample_size: int = 10) -> None:
    records = []

    for row in read_jsonl("data/raw/corpus.jsonl"):
        title = (row.get("title") or "").strip()
        body = (row.get("text") or "").strip()

        if not body:
            records.append(
                {
                    "doc_id": row.get("_id"),
                    "title": title,
                    "title_length": len(title),
                }
            )

    by_lenth = sorted(records, key=lambda row: row["title_length"])

    groups = {
        "TITLE NGẮN NHẤT": by_lenth[:sample_size],
        "MẪU NGẪU NHIÊN": random.Random(42).sample(
            records,
            min(sample_size, len(records)),
        ),
        "TITLE DÀI NHẤT": by_lenth[-sample_size:],
    }

    for group_name, group in groups.items():
        print(f"\n=== {group_name} ===")

        for row in group:
            print(
                f"\nID: {row['doc_id']}"
                f"\nĐộ dài title: {row['title_length']}"
                f"\nTitle: {row['title']}"
            )


def export_empty_bodies() -> None:
    output = Path("artifacts/title_only_records.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        for row in read_jsonl("data/raw/corpus.jsonl"):
            if not (row.get("text") or "").strip():
                file.write(
                    json.dumps(
                        {
                            "doc_id": row.get("_id"),
                            "title": row.get("title"),
                            "title_length": len(row.get("title") or ""),
                        },
                        ensure_ascii=False,

                    ) 
                    + "\n"
                )
    print(f"\nĐã ghi {output} với các văn bản rỗng (chỉ có title).")


def main() -> None:
    profile_corpus()
    profile_qrels("train")
    profile_qrels("test")
    inspect_empty_bodies(sample_size=10)
    export_empty_bodies()

if __name__ == "__main__":
    main()
