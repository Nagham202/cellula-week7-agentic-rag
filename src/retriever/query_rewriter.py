import json
import re

import config
from src.llm import get_llm

SYSTEM_PROMPT = """You rewrite a user's question into search queries for a document search engine.
You do NOT answer the question.

Rules:
1. "query": one clear question that can be understood without the conversation. Replace words like
   "it", "its", "they", "this method", "the second one" with what they refer to in the conversation.
   If the question is already clear, keep it almost the same.
2. Expand an abbreviation only if you are sure what it means, and keep the abbreviation too:
   "RAG" -> "Retrieval-Augmented Generation (RAG)". If you are not sure, leave it as it is.
3. Keep exact terms exactly as written: file names, page, chapter and section numbers, codes (E31),
   model names (BERT-base), numbers, equation and table numbers.
4. "alternatives": up to 2 other ways to ask the same question with different words that a document
   might use (for example "disadvantages" -> "limitations", "drawbacks"). Same meaning, no new topics.
5. Never add facts, answers or information that are not in the question or the conversation.

Reply with JSON only, no other text:
{"query": "...", "alternatives": ["...", "..."]}

Examples:

Conversation:
User: What is RAG?
Assistant: RAG (Retrieval-Augmented Generation) combines a retriever with a text generator.
New question: What are its disadvantages?
{"query": "What are the disadvantages of Retrieval-Augmented Generation (RAG)?", "alternatives": ["What are the limitations of Retrieval-Augmented Generation?", "What problems or drawbacks does RAG have?"]}

Conversation: (none)
New question: What does error E31 mean?
{"query": "What does error E31 mean?", "alternatives": ["What is the cause of error code E31?", "How do I fix error E31?"]}

Conversation:
User: Which models were compared in messy_report.pdf?
Assistant: BERT-base, RoBERTa-large and DistilBERT.
New question: which one is the fastest?
{"query": "Which model is the fastest among BERT-base, RoBERTa-large and DistilBERT in messy_report.pdf?", "alternatives": ["Which of BERT-base, RoBERTa-large and DistilBERT has the best inference speed?"]}
"""


def format_history(chat_history):
    if not chat_history:
        return "(none)"
    # one turn = a question and its answer
    recent = chat_history[-2 * config.HISTORY_TURNS_FOR_REWRITER:]
    lines = []
    for message in recent:
        speaker = "User" if message["role"] == "user" else "Assistant"
        content = message["content"]
        if message["role"] != "user" and len(content) > config.HISTORY_ANSWER_LIMIT:
            content = content[:config.HISTORY_ANSWER_LIMIT] + "..."
        lines.append(f"{speaker}: {content}")
    return "\n" + "\n".join(lines)


def build_user_message(question, chat_history):
    return f"Conversation: {format_history(chat_history)}\nNew question: {question}"


def no_rewrite(question):
    return {"query": question, "alternatives": [], "rewritten": False}


def parse_rewrite(reply, question):
    # finds the json even if the model adds text or ``` around it
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if match is None:
        return no_rewrite(question)
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return no_rewrite(question)

    if not isinstance(data, dict):
        return no_rewrite(question)
    query = data.get("query")
    if not isinstance(query, str) or not query.strip():
        return no_rewrite(question)

    alternatives = []
    raw_alternatives = data.get("alternatives")
    if isinstance(raw_alternatives, list):
        for alternative in raw_alternatives:
            if isinstance(alternative, str) and alternative.strip() and alternative.strip() != query.strip():
                alternatives.append(alternative.strip())
    return {"query": query.strip(), "alternatives": alternatives[:config.MAX_ALTERNATIVE_QUERIES], "rewritten": True}


def rewrite_query(question, chat_history=None, llm=None):
    # tests pass a fake llm here
    if llm is None:
        llm = get_llm("rewriter")
    messages = [("system", SYSTEM_PROMPT), ("human", build_user_message(question, chat_history))]
    try:
        reply = llm.invoke(messages).content
    # if every provider fails we just search the original question
    except Exception:
        return no_rewrite(question)
    return parse_rewrite(reply, question)


# quick test: python -m src.retriever.query_rewriter  (5 LLM calls)
if __name__ == "__main__":
    rag_history = [
        {"role": "user", "content": "What is RAG?"},
        {"role": "assistant", "content": "RAG (Retrieval-Augmented Generation) combines a pre-trained "
                                         "retriever with a seq2seq generator such as BART."},
    ]
    kito_history = [
        {"role": "user", "content": "What does error E31 mean on the Kito robot?"},
        {"role": "assistant", "content": "E31 means the lidar sensor is blocked."},
    ]
    examples = [
        ("What are its disadvantages?", rag_history),
        ("and what about E47?", kito_history),
        ("According to chapter 4, is RAG-Token or RAG-Sequence better on FEVER?", rag_history),
        ("How is DPR trained?", None),
        ("What does Equation 12 compute?", None),
    ]
    for question, history in examples:
        result = rewrite_query(question, history)
        print(f"\nQuestion:     {question}")
        print(f"Query:        {result['query']}")
        for alternative in result["alternatives"]:
            print(f"Alternative:  {alternative}")
        print(f"Rewritten:    {result['rewritten']}")
