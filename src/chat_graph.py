from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.answer.answer_agent import generate_answer
from src.orchestrator import run_analysis


class ChatState(TypedDict):
    question: str
    chat_history: list
    search_query: str
    evidence: list
    analysis: str
    answer: str
    sources: list


def analyze_node(state):
    # Sara's orchestrator: the retriever finds the evidence, then the analyst studies it
    result = run_analysis(state["question"], state["chat_history"])
    return {
        "search_query": result["retrieval_details"].get("search_query", state["question"]),
        "evidence": result["all_evidence"],
        "analysis": result["analysis"],
    }


def answer_node(state):
    # the search query is the question written in full, so a follow-up like
    # "How do I fix it?" reaches the answer agent as "How do I fix error E31?"
    reply = generate_answer(state["search_query"], state["analysis"], state["evidence"])
    return {"answer": reply["answer"], "sources": reply["sources"]}


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("answer", answer_node)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


chat_graph = build_graph()


def ask(question, chat_history=None):
    # the one function the streamlit app calls
    state = chat_graph.invoke({"question": question, "chat_history": chat_history or []})
    return {"answer": state["answer"], "sources": state["sources"]}


# quick test: python -m src.chat_graph  (needs the database, makes a few LLM calls)
if __name__ == "__main__":
    history = []
    for question in ["What does error E31 mean?", "How do I fix it?"]:
        reply = ask(question, history)
        print(f"=== {question}\n{reply['answer']}\n")
        # the history is kept oldest first, the same way the app will keep it
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reply["answer"]})
