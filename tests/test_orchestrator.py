from src import orchestrator


def test_orchestrator_no_evidence(monkeypatch):

    monkeypatch.setattr(
        orchestrator,
        "retrieve_with_details",
        lambda **kwargs: {
            "evidence": [],
            "search_query": kwargs["question"],
            "alternative_queries": [],
            "rewritten": False,
            "filters": {},
            "filters_relaxed": False
        }
    )

    result = orchestrator.run_analysis(
        "Question about information not in the documents"
    )

    assert result["initial_evidence"] == []
    assert result["additional_evidence"] == []
    assert result["all_evidence"] == []
    assert result["analysis"] == "No relevant evidence was found."

    print("\nNo-evidence test passed!")

def test_retriever_to_analyst():
    question = "How does RAG perform on fact verification?"

    result = orchestrator.run_analysis(question)

    print("\nInitial evidence:", len(result["initial_evidence"]))
    print("Additional evidence:", len(result["additional_evidence"]))
    print("Total unique evidence:", len(result["all_evidence"]))

    assert result["question"] == question
    assert len(result["initial_evidence"]) > 0
    assert isinstance(result["additional_evidence"], list)
    assert result["analysis"]
    assert len(result["all_evidence"]) == len({
        item["chunk_id"] for item in result["all_evidence"]
    })
