from src.retriever.reranker import rerank
from src.retriever.selector import select_context


def make_evidence(chunk_id, source, text, score=0.5):
    return {"chunk_id": chunk_id, "source": source, "page": 1, "text": text, "score": score}


def test_reranker_puts_the_relevant_chunk_first_with_scores_from_0_to_1():
    candidates = [
        make_evidence("a", "faq.txt", "Support is available Sunday to Thursday from 9:00 to 17:00."),
        make_evidence("b", "manual.pdf", "Error E31: the lidar sensor is blocked. Clean the sensor."),
        make_evidence("c", "policy.docx", "Employees get 21 days of paid annual leave per year."),
    ]
    reranked = rerank("What does error E31 mean?", candidates)
    assert reranked[0]["chunk_id"] == "b"
    assert all(0 <= item["score"] <= 1 for item in reranked)
    assert [item["score"] for item in reranked] == sorted((item["score"] for item in reranked), reverse=True)


def test_selector_skips_near_copies():
    text = "RAG combines a pre-trained retriever with a pre-trained seq2seq generator."
    evidence = [
        make_evidence("a", "paper.pdf", text, 0.9),
        make_evidence("b", "copy.pdf", text, 0.8),
        make_evidence("c", "manual.pdf", "Clean the lidar sensor once a week with a dry cloth.", 0.7),
    ]
    assert [item["chunk_id"] for item in select_context(evidence, top_k=3)] == ["a", "c"]


def test_selector_covers_every_named_file_first():
    evidence = [make_evidence(f"a{number}", "a.pdf", f"Fact number {number} about apples and trees.", 0.9 - number / 100)
                for number in range(5)]
    evidence.append(make_evidence("b0", "b.pdf", "Bananas grow in warm countries near the sea.", 0.1))
    chosen = select_context(evidence, top_k=3, must_cover_sources=["a.pdf", "b.pdf"])
    assert "b0" in [item["chunk_id"] for item in chosen]
    assert len(chosen) == 3


def test_selector_respects_the_size_budget_but_keeps_at_least_one():
    evidence = [make_evidence(name, "a.pdf", f"{name} " + "word " * 200, 0.9) for name in ["x", "y", "z"]]
    assert len(select_context(evidence, top_k=3, max_characters=1500)) == 1
    assert len(select_context(evidence, top_k=3, max_characters=10)) == 1


def test_selector_never_returns_more_than_max_evidence():
    evidence = [make_evidence(str(number), "a.pdf", f"Topic {number}: " + " ".join([str(number)] * 5), 0.5)
                for number in range(20)]
    assert len(select_context(evidence, top_k=50, max_characters=100000, max_similarity=1.1)) == 8
