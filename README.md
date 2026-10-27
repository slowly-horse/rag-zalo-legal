# RAG Tra cứu Luật Việt Nam

Hệ thống retrieval cho văn bản pháp luật Việt Nam, xây theo hướng **đo được – gỡ lỗi được –
cải thiện được**.

## Baseline

**Baseline** — BM25 (underthesea) trên toàn bộ 61.425 Điều, cả 788 câu test, không cần API
key: **Recall@10 0,8610 · MRR@10 0,5785**, p95 1,18 ms ([chi tiết](reports/week2.md)).

Đây là **con số duy nhất để so**. Dense, hybrid, rerank, graph — mọi retriever thêm vào từ
đây đều phải đánh bại BM25 trên cùng 788 câu đó, nếu không thì nó không đáng chi phí.
Lexical là baseline chuẩn của mọi benchmark retrieval thực tế (BEIR, MTEB) vì lý do này:
rẻ, tất định, không cần model, và khó đánh bại hơn người ta tưởng.

## Dataset

[`GreenNode/zalo-ai-legal-text-retrieval-vn`](https://huggingface.co/datasets/GreenNode/zalo-ai-legal-text-retrieval-vn)
pin ở commit `12d76d4d…`, format BEIR/MTEB: 61.425 Điều · 3.196 câu hỏi · 3.298 nhãn.
Corpus id dạng `01/2009/tt-bnn+1` = `<số>/<năm>/<mã>+<chỉ số Điều>` → suy ra loại văn bản,
năm, cơ quan ban hành.

Bốn điều dataset **không** giống giả định ban đầu (chi tiết ở [plan §1b](docs/plan.md)):
corpus đã chunk sẵn ở mức Điều · 97% câu chỉ có 1 nhãn đúng và nhãn là binary · có leakage
train↔test · `queries.jsonl` có 102 dòng trùng.