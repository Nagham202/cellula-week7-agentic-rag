import config
from src.pipeline import store
from src.retriever.search import hybrid_search, keyword_search, semantic_search

CHUNKS = [
    {"source": "manual.pdf", "type": "pdf", "page": 3, "section": None, "chapter": None, "chunk_id": "manual.pdf_p3_c1",
     "text": "Source: manual.pdf, page 3\nError E31: lidar sensor blocked. Clean the sensor."},
    {"source": "manual.pdf", "type": "pdf", "page": 4, "section": None, "chapter": None, "chunk_id": "manual.pdf_p4_c2",
     "text": "Source: manual.pdf, page 4\nError E12: battery overheating. Let the robot cool down."},
    {"source": "faq.txt", "type": "txt", "page": None, "section": None, "chapter": None, "chunk_id": "faq.txt_c1",
     "text": "Source: faq.txt\nThe warranty lasts two years. Batteries are covered for one year."},
]


def fill_temporary_database(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "QDRANT_PATH", str(tmp_path / "qdrant"))
    monkeypatch.setattr(store, "client", None)
    store.add_chunks(CHUNKS[:2])
    store.add_chunks(CHUNKS[2:])


def test_keyword_search_finds_the_exact_code(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    results = keyword_search("What is E31?", top_k=3)
    assert results[0]["chunk_id"] == "manual.pdf_p3_c1"


def test_semantic_search_finds_the_meaning(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    results = semantic_search("How long is the guarantee?", top_k=3)
    assert results[0]["chunk_id"] == "faq.txt_c1"


def test_hybrid_returns_evidence_in_the_agreed_format(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    results = hybrid_search("lidar error E31", top_k=2)
    assert len(results) == 2
    assert results[0]["chunk_id"] == "manual.pdf_p3_c1"
    for evidence in results:
        assert {"source", "page", "text", "score", "chunk_id"} <= set(evidence)
