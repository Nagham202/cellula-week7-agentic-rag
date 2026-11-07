import config
from src.pipeline import store
from src.retriever.filters import build_filter, extract_filters, relax_filters
from src.retriever.search import hybrid_search

SOURCES = ["rag_paper.pdf", "messy_report.pdf", "hr_policy.docx"]


def test_file_name_with_or_without_extension_or_underscore():
    assert extract_filters("What does rag_paper.pdf say?", SOURCES) == {"sources": ["rag_paper.pdf"]}
    assert extract_filters("In the RAG paper, what is DPR?", SOURCES) == {"sources": ["rag_paper.pdf"]}
    assert extract_filters("Compare messy_report and rag_paper", SOURCES)["sources"] == ["rag_paper.pdf", "messy_report.pdf"]


def test_unknown_file_names_are_never_invented():
    assert extract_filters("What does paper.pdf say about BERT?", SOURCES) == {}


def test_pages_and_chapters():
    assert extract_filters("What is on page 4?", SOURCES) == {"pages": [4, 4]}
    assert extract_filters("Summarize pages 2 to 5", SOURCES) == {"pages": [2, 5]}
    assert extract_filters("Summarize pages 2-5", SOURCES) == {"pages": [2, 5]}
    assert extract_filters("According to Chapter 4, ...", SOURCES) == {"chapter": "4"}
    assert extract_filters("What does section 4.2 say?", SOURCES) == {"chapter": "4"}
    assert extract_filters("What is in appendix g?", SOURCES) == {"chapter": "G"}


def test_question_without_filter_words():
    assert extract_filters("How does RAG work?", SOURCES) == {}
    assert build_filter({}) is None


def test_relax_keeps_only_the_file_names():
    assert relax_filters({"sources": ["hr_policy.docx"], "pages": [2, 2]}) == {"sources": ["hr_policy.docx"]}
    assert relax_filters({"chapter": "4"}) == {}


def test_filtered_search_only_returns_matching_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "QDRANT_PATH", str(tmp_path / "qdrant"))
    monkeypatch.setattr(store, "client", None)
    for source in ["a.pdf", "b.pdf"]:
        store.add_chunks([
            {"source": source, "type": "pdf", "page": page, "section": None, "chapter": str(page),
             "chunk_id": f"{source}_p{page}_c{page}", "text": f"Source: {source}, page {page}\nThe model accuracy is high."}
            for page in [1, 2, 3]
        ])

    results = hybrid_search("model accuracy", top_k=10, query_filter=build_filter({"sources": ["b.pdf"], "pages": [2, 3]}))
    assert sorted(evidence["chunk_id"] for evidence in results) == ["b.pdf_p2_c2", "b.pdf_p3_c3"]

    results = hybrid_search("model accuracy", top_k=10, query_filter=build_filter({"chapter": "1"}))
    assert sorted(evidence["chunk_id"] for evidence in results) == ["a.pdf_p1_c1", "b.pdf_p1_c1"]
