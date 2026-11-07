import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

QDRANT_PATH = "data/qdrant"
COLLECTION_NAME = "documents"

# 500/100 was better than 800/150 in week 6
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# if you change the model, delete data/qdrant and ingest again (old vectors won't match)
DENSE_MODEL = "BAAI/bge-small-en-v1.5"
# bge finds passages better when the question starts with this
DENSE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
DENSE_VECTOR_NAME = "dense"
SPARSE_MODEL = "Qdrant/bm25"
SPARSE_VECTOR_NAME = "bm25"

HYBRID_CANDIDATES = 20
TOP_K = 6

USE_RERANKER = True
RERANKER_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
RERANK_CANDIDATES = 20

MAX_EVIDENCE = 8
# about 1,100 tokens, keeps the analyst's prompt small
MAX_CONTEXT_CHARACTERS = 4500
DUPLICATE_SIMILARITY = 0.92

USE_QUERY_REWRITER = True
HISTORY_TURNS_FOR_REWRITER = 3
HISTORY_ANSWER_LIMIT = 400
MAX_ALTERNATIVE_QUERIES = 2

# "groq", "openrouter" or "ollama", the others are used as fallbacks
LLM_PROVIDER = "groq"
USE_FALLBACKS = True
LLM_TEMPERATURE = 0

# groq limits are per model, so each agent gets its own
GROQ_MODELS = {
    "rewriter": "openai/gpt-oss-20b",
    "analyst": "openai/gpt-oss-120b",
    "answer": "openai/gpt-oss-120b",
}
# gpt-oss's hidden thinking tokens count against the limit, low cuts them
GROQ_REASONING_EFFORT = "low"
# free models change often, check openrouter.ai/models?max_price=0 if one stops working
OPENROUTER_MODELS = {
    "rewriter": "nvidia/nemotron-3.5-lightning:free",
    "analyst": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "answer": "nvidia/nemotron-3-ultra-550b-a55b:free",
}
OLLAMA_MODEL = "llama3.1:8b"
