from src import chat_graph

FAKE_EVIDENCE = [{"source": "kito_manual.pdf", "page": 3, "text": "Error E31: lidar sensor blocked.",
                  "chunk_id": "kito_manual.pdf_p3_c1"}]


def fake_run_analysis(question, chat_history=None, top_k=6):
    return {
        "all_evidence": FAKE_EVIDENCE,
        "analysis": "E31 means the lidar sensor is blocked.",
        "retrieval_details": {"search_query": "How do I fix error E31 on the Kito robot?"},
    }


def test_graph_gives_answer_and_sources(monkeypatch):
    monkeypatch.setattr(chat_graph, "run_analysis", fake_run_analysis)
    monkeypatch.setattr(chat_graph, "generate_answer",
                        lambda question, analysis, evidence: {"answer": "Clean the sensor.",
                                                              "sources": ["kito_manual.pdf, page 3"]})
    reply = chat_graph.ask("How do I fix it?")
    assert reply == {"answer": "Clean the sensor.", "sources": ["kito_manual.pdf, page 3"]}


def test_answer_agent_gets_the_full_question(monkeypatch):
    received = {}

    def fake_generate_answer(question, analysis, evidence):
        received["question"] = question
        received["evidence"] = evidence
        return {"answer": "Clean the sensor.", "sources": []}

    monkeypatch.setattr(chat_graph, "run_analysis", fake_run_analysis)
    monkeypatch.setattr(chat_graph, "generate_answer", fake_generate_answer)
    chat_graph.ask("How do I fix it?", [{"role": "user", "content": "What does error E31 mean?"}])
    assert received["question"] == "How do I fix error E31 on the Kito robot?"
    assert received["evidence"] == FAKE_EVIDENCE
