# Chat with your documents: three agents

Cellula Technologies NLP internship, week 7. A team project: upload PDF, DOCX or TXT files and ask
questions. An Orchestrator coordinates three agents: the **Retriever** finds evidence, the
**Analyst** reasons over it, and the **Answer Agent** writes the final answer with citations.

| Part | Owner | Folder |
|---|---|---|
| Document pipeline + Retriever Agent | Nagham | `src/pipeline/`, `src/retriever/` |
| Analyst Agent, Orchestrator | Sara | `src/analyst/` |
| Answer Agent, Streamlit app | | `src/answer/`, `app.py` |
| Shared | everyone | `config.py`, `src/llm.py` |

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then put your own GROQ_API_KEY and OPENROUTER_API_KEY in .env
python -m src.llm                 # checks groq, openrouter and ollama with one short call each
python -m src.pipeline.ingest     # builds your local database from data/samples (about 5 s)
```

Always run scripts from the project folder with `python -m ...`, so `config` and `src` can be found.
The first run downloads three small local models (embeddings 67 MB, BM25, reranker 80 MB).

---

## Document pipeline + Retriever Agent (Nagham)

### What it does

```
upload:    file -> load -> clean -> chunk (500/100 + metadata) -> dense + BM25 vectors -> Qdrant
question:  query rewriter -> metadata filter -> hybrid search (20 candidates) -> reranker -> context selector -> evidence
```

The Retriever **only finds evidence; it never answers**.

### Uploading files (for the Streamlit app)

```python
from src.pipeline.ingest import ingest_file
from src.pipeline.loaders import SourceError
from src.pipeline.store import count_chunks, delete_source, list_sources

try:
    chunk_count = ingest_file("data/uploads/paper.pdf")   # uploading the same file name again replaces its old chunks
except SourceError as error:
    print(error)                                          # a message you can show the user (broken file, wrong type, scanned PDF...)

list_sources()                 # ["kito_manual.pdf", "paper.pdf", ...]
count_chunks()                 # all chunks, or count_chunks("paper.pdf")
delete_source("paper.pdf")     # for a "remove file" button
```

### Getting evidence (for the Orchestrator and the Analyst)

```python
from src.retriever.retriever import retrieve, retrieve_more, retrieve_with_details

evidence = retrieve(question, chat_history=None, top_k=6, filters=None)          # Orchestrator
more = retrieve_more(specific_query, already_seen_ids=[...], top_k=4)            # Analyst feedback loop
details = retrieve_with_details(question, chat_history)                          # evidence + how we searched
```

- **`chat_history`**: the conversation so far, oldest first (the same format as Streamlit chat):
  `[{"role": "user", "content": "What is RAG?"}, {"role": "assistant", "content": "RAG is ..."}]`.
  It is used to understand follow-up questions like "What are its disadvantages?".
- **`filters`** (optional, e.g. from a "search only in" dropdown):
  `{"sources": ["paper.pdf"], "pages": [2, 4], "chapter": "4"}`. If you don't pass filters, they are
  read from the question: "According to Chapter 4 of paper.pdf ..." -> `{"sources": ["paper.pdf"], "chapter": "4"}`.
  If a filter matches nothing (e.g. "page 2" of a DOCX, which has no pages), the search is retried
  with only the file names, and `retrieve_with_details` returns `"filters_relaxed": true`.
- **`retrieve_more`** never returns a chunk whose `chunk_id` is in `already_seen_ids`, so the
  Analyst always gets new evidence. It does not call the LLM.

### Evidence format

Each item has the 5 agreed keys (`source`, `page`, `text`, `score`, `chunk_id`) plus `type`, `section`, `chapter`:

- `page` is `None` for DOCX and TXT (they have no pages): cite only the file name.
- `section` is the heading the chunk is under, e.g. `"4.4 Fact Verification"` (or `None`).
- `text` starts with a citation header, e.g. `Source: paper.pdf, page 6, section: 4.4 Fact Verification`.
- `score` is the reranker's relevance from 0 to 1, best first. A very low score (< 0.05) usually means
  "not relevant", but related chunks often all get ~0.99, so a high score alone does not prove the
  evidence is enough. Judge the text.

Example: `retrieve_with_details("What does error E31 mean?", top_k=2)` (texts shortened):

```json
{
  "evidence": [
    {
      "source": "kito_manual.pdf", "type": "pdf", "page": 3, "section": null, "chapter": null,
      "chunk_id": "kito_manual.pdf_p3_c3",
      "text": "Source: kito_manual.pdf, page 3\nKito User Manual - Page 3: Maintenance and error codes\n...",
      "score": 0.9905
    },
    {
      "source": "rag_paper.pdf", "type": "pdf", "page": 12, "section": "References", "chapter": null,
      "chunk_id": "rag_paper.pdf_p12_c124",
      "text": "Source: rag_paper.pdf, page 12, section: References\nH. Wallach, H. Larochelle, ...",
      "score": 0.0
    }
  ],
  "search_query": "What does error E31 mean?",
  "alternative_queries": ["What is the cause of error code E31?", "How do I fix error E31?"],
  "rewritten": true,
  "filters": {},
  "filters_relaxed": false
}
```

### Using it as a LangChain tool (optional, if the Orchestrator or Analyst uses tool calling)

```python
from langchain_core.tools import tool
from src.retriever.retriever import retrieve_more

@tool
def search_more_evidence(query: str, already_seen_ids: list[str]) -> list[dict]:
    """Find NEW evidence in the uploaded documents for a specific query."""
    return retrieve_more(query, already_seen_ids=already_seen_ids)
```

### Tests without Qdrant or models

```python
from src.retriever.fake_retriever import retrieve, retrieve_more   # same functions, hard-coded evidence
```

### Settings in `config.py` (my part)

| Setting | Value | Meaning |
|---|---|---|
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | 500, 100 | characters per chunk |
| `DENSE_MODEL` | `BAAI/bge-small-en-v1.5` | if changed: delete `data/qdrant` and ingest again |
| `TOP_K`, `MAX_EVIDENCE` | 6, 8 | default and maximum evidence items |
| `USE_QUERY_REWRITER` | `True` | 1 LLM call per `retrieve()` (Groq model of the "rewriter" role) |
| `USE_RERANKER` | `True` | `Xenova/ms-marco-MiniLM-L-6-v2`, about 85 ms per question, local |
| `RERANK_CANDIDATES` | 20 | candidates from hybrid search before reranking |
| `MAX_CONTEXT_CHARACTERS` | 4500 | size budget of the evidence list (~1,100 tokens) |

### Good to know

- **Qdrant local mode allows one program at a time** on `data/qdrant`. If you get
  "Qdrant could not open data/qdrant", close the other program (e.g. the Streamlit app) and try again.
- `data/qdrant` is not in git: everyone builds their own with `python -m src.pipeline.ingest`.
- Free OpenRouter models change often; run `python -m src.llm` before a demo.

### Checks

```bash
python -m pytest -q                    # 50 tests, no LLM calls
python -m scripts.check_end_to_end     # upload -> ask -> re-upload -> delete (3 LLM calls)
python -m eval.compare_search          # semantic vs keyword vs hybrid vs rewriter vs reranker
python -m eval.compare_rerankers       # 3 reranker models, quality and speed
```

Results (28 test questions, right document and page in the top 3): semantic 0.82, keyword 0.86,
hybrid 0.89, hybrid + query rewriter 0.93, full pipeline 0.96. Details in `eval/results/` and `report_notes.md`.
