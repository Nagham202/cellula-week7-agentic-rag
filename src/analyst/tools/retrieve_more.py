
from langchain.tools import tool

from src.retriever.retriever import retrieve_more


@tool
def retrieve_more_evidence(
    query: str,
    already_seen_ids: list[str] = None,
    top_k: int = 4
) -> list[dict]:
    """
    Retrieve additional relevant evidence from uploaded documents.

    Use this tool when the current evidence is insufficient
    to answer a question or when more information is required.

    Excludes previously retrieved chunks to avoid duplicates.
    """

    evidence = retrieve_more(
        query=query,
        already_seen_ids=already_seen_ids or [],
        top_k=top_k
    )

    return evidence
