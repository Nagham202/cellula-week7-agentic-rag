import config
from src.pipeline import store
from src.retriever import fake_retriever
from src.retriever.retriever import retrieve, retrieve_more, retrieve_with_details

AGREED_KEYS = {"source", "page", "text", "score", "chunk_id"}


def fill_temporary_database(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "QDRANT_PATH", str(tmp_path / "qdrant"))
    monkeypatch.setattr(store, "client", None)
    # no llm calls in tests, the rewriter has its own tests with a fake llm
    monkeypatch.setattr(config, "USE_QUERY_REWRITER", False)
    # different text on every page, the selector drops near-identical ones
    page_texts = [
        "The CNN reached 92% accuracy on the test set.",
        "Training took three days on four GPUs.",
        "The dataset has 50,000 labelled images of animals.",
        "Data augmentation used random crops and flips.",
        "The CNN accuracy dropped to 85% on blurry photos.",
        "We compare our CNN with a vision transformer.",
        "The learning rate was 0.001 with the Adam optimizer.",
        "Future work will test the CNN on medical images.",
    ]
    store.add_chunks([
        {"source": "paper.pdf", "type": "pdf", "page": page, "section": None, "chapter": None,
         "chunk_id": f"paper.pdf_p{page}_c{page}", "text": f"Source: paper.pdf, page {page}\n{text}"}
        for page, text in enumerate(page_texts, start=1)
    ])
    store.add_chunks([
        {"source": "policy.docx", "type": "docx", "page": None, "section": None, "chapter": None,
         "chunk_id": "policy.docx_c1", "text": "Source: policy.docx\nEmployees get 21 days of paid leave."},
    ])


def test_retrieve_returns_top_k_in_the_agreed_format(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    evidence = retrieve("What is the CNN accuracy?", top_k=3)
    assert len(evidence) == 3
    for item in evidence:
        assert AGREED_KEYS <= set(item)


def test_filter_from_question_and_from_app(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    assert {item["page"] for item in retrieve("CNN accuracy on page 4 of paper.pdf")} == {4}
    assert {item["source"] for item in retrieve("accuracy", filters={"sources": ["policy.docx"]})} == {"policy.docx"}


def test_filter_that_matches_nothing_is_relaxed(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    details = retrieve_with_details("What does page 2 of policy.docx say about leave?")
    assert details["filters_relaxed"] is True
    assert details["evidence"][0]["chunk_id"] == "policy.docx_c1"


def test_retrieve_more_never_returns_chunks_already_seen(tmp_path, monkeypatch):
    fill_temporary_database(tmp_path, monkeypatch)
    seen = [item["chunk_id"] for item in retrieve("CNN accuracy", top_k=5)]
    more = retrieve_more("CNN accuracy", already_seen_ids=seen, top_k=4)
    assert len(more) == 4
    assert not set(seen) & {item["chunk_id"] for item in more}


def test_fake_retriever_has_the_same_functions_and_format():
    for item in fake_retriever.retrieve("anything", top_k=3) + fake_retriever.retrieve_more("anything"):
        assert AGREED_KEYS <= set(item)
