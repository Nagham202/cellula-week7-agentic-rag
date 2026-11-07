import re

from qdrant_client import models

# "page 4", "pages 2-4", "pages 2 to 4"
PAGE_PATTERN = re.compile(r"\bpages?\s+(\d+)(?:\s*(?:-|to)\s*(\d+))?", re.IGNORECASE)
# "chapter 4", "section 4.2", "appendix G"
CHAPTER_PATTERN = re.compile(r"\b(?:chapter|section)\s+(\d+)|\bappendix\s+([A-H])\b", re.IGNORECASE)
# a very short name like "a.pdf" would match too many questions
MIN_NAME_LENGTH = 3


def mentioned_sources(question, sources):
    text = question.lower()
    found = []
    for source in sources:
        name = source.lower()
        name_without_extension = name.rsplit(".", 1)[0]
        if len(name_without_extension) < MIN_NAME_LENGTH:
            continue
        if name_without_extension in text or name_without_extension.replace("_", " ") in text:
            found.append(source)
    return found


def extract_filters(question, sources):
    filters = {}

    found_sources = mentioned_sources(question, sources)
    if found_sources:
        filters["sources"] = found_sources

    page_match = PAGE_PATTERN.search(question)
    if page_match is not None:
        first_page = int(page_match.group(1))
        last_page = int(page_match.group(2)) if page_match.group(2) else first_page
        filters["pages"] = [first_page, last_page]

    chapter_match = CHAPTER_PATTERN.search(question)
    if chapter_match is not None:
        filters["chapter"] = chapter_match.group(1) or chapter_match.group(2).upper()

    return filters


# used when page/chapter finds nothing, e.g. "page 2" of a docx, which has no pages
def relax_filters(filters):
    relaxed = {}
    if filters.get("sources"):
        relaxed["sources"] = filters["sources"]
    return relaxed


def build_filter(filters, exclude_chunk_ids=None):
    excluded = []
    if exclude_chunk_ids:
        excluded.append(models.FieldCondition(key="chunk_id", match=models.MatchAny(any=list(exclude_chunk_ids))))

    if filters is None:
        filters = {}

    conditions = []
    if filters.get("sources"):
        conditions.append(models.FieldCondition(key="source", match=models.MatchAny(any=filters["sources"])))
    if filters.get("pages"):
        first_page, last_page = filters["pages"]
        conditions.append(models.FieldCondition(key="page", range=models.Range(gte=first_page, lte=last_page)))
    if filters.get("chapter"):
        conditions.append(models.FieldCondition(key="chapter", match=models.MatchValue(value=filters["chapter"])))

    if not conditions and not excluded:
        return None
    return models.Filter(must=conditions, must_not=excluded)


# quick test: python -m src.retriever.filters (run python -m src.pipeline.ingest first)
if __name__ == "__main__":
    from src.pipeline.store import list_sources
    from src.retriever.search import hybrid_search

    sources = list_sources()
    print("Stored files:", sources)

    questions = [
        "According to Chapter 4 of rag_paper.pdf, how well does RAG do on fact verification?",
        "What is on page 19 of the RAG paper?",
        "What does the kito_manual say about error codes?",
        "Compare messy_report.pdf and rag_paper.pdf: can the knowledge be updated without retraining?",
        "What is in Appendix G?",
        "How does RAG do on fact verification?",
    ]
    for question in questions:
        filters = extract_filters(question, sources)
        print(f"\n=== {question}\n    filter: {filters}")
        for evidence in hybrid_search(question, top_k=3, query_filter=build_filter(filters)):
            print(f"    {evidence['chunk_id']:26s} page {evidence['page']}, section: {evidence['section']}")
