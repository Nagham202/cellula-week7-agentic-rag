import re

# a number between brackets, like [1] or [12], with the space before it
CITATION_PATTERN = re.compile(r" ?\[(\d+)\]")
# the model writes this word when the evidence does not answer the question
NOT_FOUND = "NOT_FOUND"
NOT_FOUND_MESSAGE = "I couldn't find this information in the uploaded documents."

def format_source(source, page):
    # docx and txt files have no pages, so only the file name is shown
    if page is None:
        return source
    return f"{source}, page {page}"


def attach_citations(answer, evidence):
    # the model writes [1], [2]... and each number becomes its real source
    for number, item in enumerate(evidence, start=1):
        citation = "[" + format_source(item["source"], item.get("page")) + "]"
        answer = answer.replace(f"[{number}]", citation)
    # a number with no evidence (like [7] when there are only 6) is removed
    return CITATION_PATTERN.sub("", answer)


def format_sources(answer, evidence):
    # only the evidence the answer used, each source once, in the order it was first used
    sources = []
    for text in CITATION_PATTERN.findall(answer):
        number = int(text)
        if number < 1 or number > len(evidence):
            continue
        item = evidence[number - 1]
        source = format_source(item["source"], item.get("page"))
        if source not in sources:
            sources.append(source)
    return sources

def format_response(answer, sources):
    if NOT_FOUND in answer:
        return NOT_FOUND_MESSAGE
    if not sources:
        return answer
    lines = [answer, "", "Sources:"]
    for source in sources:
        lines.append(f"- {source}")
    return "\n".join(lines)

# quick test: python -m src.answer.formatters
if __name__ == "__main__":
    evidence = [
        {"source": "kito_manual.pdf", "page": 1, "text": "Full charge time: 90 minutes at the Kito Dock."},
        {"source": "notes.docx", "page": None, "text": "The office opens at 8 am."},
    ]
    answers = [
        "Kito charges in about 90 minutes [1]. The office opens at 8 am [2].",
        "Kito is a home robot.",
        "NOT_FOUND",
    ]
    for answer in answers:
        sources = format_sources(answer, evidence)
        print(format_response(attach_citations(answer, evidence), sources))
        print("-----")