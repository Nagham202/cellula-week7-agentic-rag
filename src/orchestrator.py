import json
from src.retriever.retriever import retrieve_with_details
from src.analyst.analyst_agent import analyst_agent

def run_analysis(question, chat_history=None, top_k=6):

    retrieval_result = retrieve_with_details(
        question=question,
        chat_history=chat_history,
        top_k=top_k
    )

    evidence = retrieval_result["evidence"]

    if not evidence:
        return {
    "question": question,
    "initial_evidence": [],
    "additional_evidence": [],
    "all_evidence": [],
    "analysis": "No relevant evidence was found.",
    "retrieval_details": retrieval_result
}

    evidence_text = ""

    for item in evidence:
        evidence_text += f"""
Source: {item.get('source')}
Page: {item.get('page')}
Section: {item.get('section')}
Chunk ID: {item.get('chunk_id')}
Score: {item.get('score')}

Content:
{item.get('text')}

-------------------------
"""

    prompt = f"""
    User Question:
    {question}

    Initial Retrieved Evidence:
    {evidence_text}

    Already Retrieved Chunk IDs:
    {[item.get('chunk_id') for item in evidence]}

    Analyze the provided evidence to answer the question.

    If more information is needed, use the
    retrieve_more_evidence tool. Exclude the chunk IDs
    already retrieved.

    Do not invent information.
    Explain your findings and mention any missing evidence.
    """

    result = analyst_agent.invoke({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    additional_evidence = []

    for message in result["messages"]:

        if getattr(message, "name", None) == "retrieve_more_evidence":

            content = message.content

            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    continue

            if isinstance(content, list):
                additional_evidence.extend(content)

    all_evidence = []
    seen_ids = set()

    for item in evidence + additional_evidence:
        chunk_id = item.get("chunk_id")

        if chunk_id and chunk_id not in seen_ids:
            all_evidence.append(item)
            seen_ids.add(chunk_id)


    analysis = result["messages"][-1].content

    return {
        "question": question,
        "initial_evidence": evidence,
        "additional_evidence": additional_evidence,
        "all_evidence": all_evidence,
        "analysis": analysis,
        "retrieval_details": retrieval_result
    }
