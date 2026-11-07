import config
from src.pipeline.store import list_sources
from src.retriever.filters import build_filter, extract_filters, relax_filters
from src.retriever.query_rewriter import no_rewrite, rewrite_query
from src.retriever.reranker import rerank
from src.retriever.search import hybrid_search
from src.retriever.selector import select_context


def search_with_fallback(query, filters, top_k, exclude_chunk_ids=None, extra_queries=None):
    evidence = hybrid_search(query, top_k=top_k, query_filter=build_filter(filters, exclude_chunk_ids),
                             extra_queries=extra_queries)
    filters_relaxed = False

    # e.g. "page 2" of a docx, which has no pages, so try again with just the file names
    if not evidence and filters:
        relaxed = relax_filters(filters)
        if relaxed != filters:
            evidence = hybrid_search(query, top_k=top_k, query_filter=build_filter(relaxed, exclude_chunk_ids),
                                     extra_queries=extra_queries)
            filters_relaxed = True
    return evidence, filters_relaxed


def rerank_and_select(query, candidates, top_k, filters):
    if config.USE_RERANKER:
        candidates = rerank(query, candidates)
    # a comparison question needs evidence from every file it names
    must_cover_sources = None
    if filters and len(filters.get("sources", [])) > 1:
        must_cover_sources = filters["sources"]
    return select_context(candidates, top_k=top_k, must_cover_sources=must_cover_sources)


def retrieve_with_details(question, chat_history=None, top_k=config.TOP_K, filters=None):
    if config.USE_QUERY_REWRITER:
        rewrite = rewrite_query(question, chat_history)
    else:
        rewrite = no_rewrite(question)

    # the original question is searched too, in case the rewrite went wrong
    extra_queries = list(rewrite["alternatives"])
    if question != rewrite["query"]:
        extra_queries.append(question)

    # the file name might only be in the chat history, so the rewrite is checked too
    if filters is None:
        filters = extract_filters(question + " " + rewrite["query"], list_sources())

    # more candidates than needed, so the reranker and the selector have something to choose from
    candidates, filters_relaxed = search_with_fallback(rewrite["query"], filters, config.RERANK_CANDIDATES,
                                                       extra_queries=extra_queries)
    evidence = rerank_and_select(rewrite["query"], candidates, top_k, filters)
    return {
        "evidence": evidence,
        "search_query": rewrite["query"],
        "alternative_queries": rewrite["alternatives"],
        "rewritten": rewrite["rewritten"],
        "filters": filters,
        "filters_relaxed": filters_relaxed,
    }


def retrieve(question, chat_history=None, top_k=config.TOP_K, filters=None):
    return retrieve_with_details(question, chat_history, top_k, filters)["evidence"]


def retrieve_more(query, already_seen_ids=None, top_k=4):
    # no rewriter here, the analyst's query is already specific
    filters = extract_filters(query, list_sources())
    candidates, _ = search_with_fallback(query, filters, config.RERANK_CANDIDATES, exclude_chunk_ids=already_seen_ids)
    return rerank_and_select(query, candidates, top_k, filters)


# quick test: python -m src.retriever.retriever (run python -m src.pipeline.ingest first)
if __name__ == "__main__":
    def show(evidence_list):
        for evidence in evidence_list:
            print(f"    {evidence['score']:.3f}  {evidence['chunk_id']:26s} section: {evidence['section']}")

    question = "How does RAG do on fact verification?"
    print(f"=== retrieve: {question}")
    first = retrieve(question)
    show(first)

    seen = [evidence["chunk_id"] for evidence in first]
    print("\n=== retrieve_more: 'FEVER label accuracy of RAG compared to BART' (leaving out the 6 above)")
    more = retrieve_more("FEVER label accuracy of RAG compared to BART", already_seen_ids=seen)
    show(more)
    print("    new chunks only:", not set(seen) & {evidence["chunk_id"] for evidence in more})

    print("\n=== retrieve_with_details: page 2 of hr_policy.docx (DOCX has no pages)")
    details = retrieve_with_details("What does page 2 of hr_policy.docx say about leave?", top_k=2)
    print(f"    filters: {details['filters']}, relaxed: {details['filters_relaxed']}")
    show(details["evidence"])

    print("\n=== retrieve with a filter from the app: only messy_report.pdf")
    show(retrieve("Which model is the best?", top_k=2, filters={"sources": ["messy_report.pdf"]}))

    print("\n=== comparison question: both files must be covered")
    show(retrieve("Compare kito_manual.pdf and rag_paper.pdf: what are their main topics?", top_k=4))
