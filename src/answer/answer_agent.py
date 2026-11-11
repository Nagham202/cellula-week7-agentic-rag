import re

from src.answer.formatters import (
    NOT_FOUND,
    NOT_FOUND_MESSAGE,
    attach_citations,
    format_response,
    format_source,
    format_sources,
)
from src.llm import get_llm

ERROR_MESSAGE = "Sorry, the answer could not be generated right now. Please try again."

SYSTEM_PROMPT = """You are the Answer Agent of a system that answers questions about the user's documents.
You get the user's question, an analysis written by an Analyst Agent, and numbered evidence from the documents.
Write the final answer for the user.

Rules:
- Use only the evidence and the analysis. Do not add facts from your own knowledge.
- After each fact, write the number of the evidence it comes from, like [1]. For two pieces of evidence write [1][3]. Use normal square brackets, never 【1】.
- Do not copy source marks or chunk ids from the analysis. Cite only with the evidence numbers.
- Do not write a list of sources at the end. It is added automatically.
- Write clear short paragraphs or a numbered list. When you compare several items or show several numbers, use a Markdown table.
- If the evidence answers only part of the question, answer that part and say what is missing.
- If the evidence does not answer the question at all, reply with exactly: NOT_FOUND"""


def number_evidence(evidence):
    # gives the model each piece of evidence with its number, like:
    # [1] kito_manual.pdf, page 1
    # Full charge time: 90 minutes at the Kito Dock.
    blocks = []
    for number, item in enumerate(evidence, start=1):
        source = format_source(item["source"], item.get("page"))
        blocks.append(f"[{number}] {source}\n{item['text']}")
    return "\n\n".join(blocks)


def build_user_message(question, analysis, evidence):
    return (f"Question:\n{question}\n\n"
            f"Analysis:\n{analysis}\n\n"
            f"Evidence:\n{number_evidence(evidence)}")


def generate_answer(question, analysis, evidence, llm=None):
    # nothing was found, so there is nothing for the model to write from
    if not evidence:
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    # tests pass a fake llm here
    if llm is None:
        llm = get_llm("answer")
    messages = [("system", SYSTEM_PROMPT), ("human", build_user_message(question, analysis, evidence))]
    try:
        answer = llm.invoke(messages).content
    # every provider failed
    except Exception:
        return {"answer": ERROR_MESSAGE, "sources": []}

    # gpt-oss models like to write 【1】 stuck to the word before it,
    # so it is changed to " [1]" before the formatters
    answer = re.sub(r" ?【", " [", answer).replace("】", "]")

    if NOT_FOUND in answer:
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    # the sources are read first, while the answer still has the numbers
    sources = format_sources(answer, evidence)
    answer = attach_citations(answer, evidence)
    return {"answer": format_response(answer, sources), "sources": sources}


# quick test: python -m src.answer.answer_agent  (needs the database, makes a few LLM calls)
if __name__ == "__main__":
    from src.orchestrator import run_analysis

    for question in ["How long does it take to fully charge Kito?", "What is the capital of France?"]:
        result = run_analysis(question)
        reply = generate_answer(result["question"], result["analysis"], result["all_evidence"])
        print(f"=== {question}\n{reply['answer']}\n")
