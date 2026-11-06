# Report Notes: Document Pipeline + Retriever Agent (Nagham)

## Decisions

### Retriever design: fixed pipeline (not an LLM agent)
- Chosen: `retrieve()` always runs rewrite -> hybrid search -> rerank -> select.
- Alternative: an LLM agent that chooses which tools to call.
- Why: simpler to debug and test piece by piece, fewer LLM calls (free-tier limits),
  predictable results. The task requires the Retriever to *use* these tools, not
  that an LLM must choose them. Agent-like behavior comes from the Analyst's
  feedback loop (`retrieve_more`).

### Work order change
- Moved the fake retriever to Step 1 so teammates can start building the Analyst
  and Answer agents right away, using the agreed evidence format.
- The fake lives in the final file (`src/retriever/retriever.py`) with the final
  function names, so teammates' import line never changes when the real search
  replaces it. Fake data includes the CNN 92/95/89 example (for the Analyst's
  calculator), a DOCX item with page None (for the Answer Agent's citations), and
  one extra item only reachable via `retrieve_more` (for the feedback loop).

## Setup
- Python 3.12 venv, packages in requirements.txt (LLM packages added at Step 7).
- Shared config.py: QDRANT_PATH, COLLECTION_NAME, CHUNK_SIZE=500, CHUNK_OVERLAP=100,
  SPARSE_MODEL="Qdrant/bm25", TOP_K=6, LLM_PROVIDER. DENSE_MODEL decided at Step 4.

## Agreed formats (pending team confirmation)
- Chunk payload: {source, type, page, chunk_id, text}
- Evidence item: {source, page, text, score, chunk_id}
- `retrieve(question, chat_history=None, top_k=6)`
- `retrieve_more(query, already_seen_ids=None, top_k=4)`

## Open questions for the team
- Are the reranker and context selector mine?
- `page = None` for DOCX/TXT: how does the Answer Agent cite them?
- Who writes the shared LLM helper that reads `LLM_PROVIDER`?
- Embedding model (decide at Step 4).

## Results

## Challenges
