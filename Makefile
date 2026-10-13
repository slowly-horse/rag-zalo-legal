DATASET_ID := GreenNode/zalo-ai-legal-text-retrieval-vn
REVISION := 12d76d4d04b94ceada970fcfbe7fec20bfa97389
RAW_DIR := data/raw

RAW_FILES := \
	corpus.jsonl \
	queries.jsonl \
	qrels/train.jsonl \
	qrels/test.jsonl 

.PHONY: fetch inspect sample profile

fetch:
	uv run hf download \
		$(DATASET_ID) \
		$(RAW_FILES) \
		--repo-type dataset \
		--revision $(REVISION) \
		--local-dir $(RAW_DIR) 

inspect:
	find $(RAW_DIR) -maxdepth 2 -type f
	wc -l $(addprefix $(RAW_DIR)/,$(RAW_FILES))

sample:
	head -n 1 $(RAW_DIR)/corpus.jsonl \
		| uv run python -m json.tool --no-ensure-ascii
	head -n 1 $(RAW_DIR)/queries.jsonl \
		| uv run python -m json.tool --no-ensure-ascii
	head -n 1 $(RAW_DIR)/qrels/train.jsonl \
		| uv run python -m json.tool --no-ensure-ascii
		
profile:
	uv run python scripts/profile_data.py