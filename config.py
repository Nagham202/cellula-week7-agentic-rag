"""Shared settings for the whole team. Change a value here, not in your own file."""

# Vector database (Qdrant local mode, no Docker)
QDRANT_PATH = "data/qdrant"
COLLECTION_NAME = "documents"

# Chunking (Week 6 result: 500/100 was better than 800/150)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Embeddings (decided at Step 4)
DENSE_MODEL = None
SPARSE_MODEL = "Qdrant/bm25"

# Retrieval
TOP_K = 6

# LLM provider: "groq", "openrouter" or "ollama"
LLM_PROVIDER = "groq"
