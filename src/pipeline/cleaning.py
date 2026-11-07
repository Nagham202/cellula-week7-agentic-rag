import unicodedata

from langchain_core.documents import Document

# pypdf doesn't keep the position, so a footer can come out at the top or the bottom
EDGE_LINES = 2
# with fewer pages a repeated line could just be a coincidence
MIN_PAGES_FOR_HEADERS = 3


def normalize_text(text):
    # turns look-alike characters into normal ones: "ﬁ" -> "fi", non-breaking space -> space
    text = unicodedata.normalize("NFKC", text)

    lines = []
    for line in text.split("\n"):
        line = " ".join(line.split())
        # at most one empty line in a row
        if line == "" and lines and lines[-1] == "":
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def line_pattern(line):
    # "Page 3 of 19" and "Page 12 of 19" both become "Page # of #"
    pattern = ""
    for character in line:
        if not character.isdigit():
            pattern += character
        elif not pattern.endswith("#"):
            pattern += "#"
    return pattern


def edge_positions(lines):
    filled = [position for position, line in enumerate(lines) if line != ""]
    return set(filled[:EDGE_LINES] + filled[-EDGE_LINES:])


def find_repeated_patterns(page_texts):
    counts = {}
    for text in page_texts:
        lines = text.split("\n")
        # a set, so a line at both the top and bottom of a short page counts once
        patterns_on_this_page = set()
        for position in edge_positions(lines):
            patterns_on_this_page.add(line_pattern(lines[position]))
        for pattern in patterns_on_this_page:
            counts[pattern] = counts.get(pattern, 0) + 1

    repeated = set()
    for pattern, count in counts.items():
        if count >= len(page_texts) / 2:
            repeated.add(pattern)
    return repeated


def remove_repeated_lines(text, repeated_patterns):
    lines = text.split("\n")
    edges = edge_positions(lines)
    kept = []
    for position, line in enumerate(lines):
        # the same text in the middle of a page is real content, so only the edges are checked
        if position in edges and line_pattern(line) in repeated_patterns:
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def join_broken_lines(text):
    joined = []
    for line in text.split("\n"):
        # a small letter at the start means the sentence continues,
        # but not after ":" (an equation or a list comes next)
        if joined and joined[-1] != "" and not joined[-1].endswith(":") and line != "" and line[0].islower():
            previous = joined[-1]
            if previous.endswith("-"):
                joined[-1] = previous[:-1] + line
            else:
                joined[-1] = previous + " " + line
        else:
            joined.append(line)
    return "\n".join(joined)


def clean_documents(documents):
    texts = [normalize_text(document.page_content) for document in documents]

    is_pdf = len(documents) > 0 and documents[0].metadata["type"] == "pdf"
    if is_pdf and len(documents) >= MIN_PAGES_FOR_HEADERS:
        repeated = find_repeated_patterns(texts)
        texts = [remove_repeated_lines(text, repeated) for text in texts]

    cleaned = []
    for document, text in zip(documents, texts):
        text = join_broken_lines(text)
        # usually a page that only had a header and a page number
        if text.strip() == "":
            continue
        cleaned.append(Document(page_content=text, metadata=document.metadata))
    return cleaned


# quick test: python -m src.pipeline.cleaning
if __name__ == "__main__":
    from pathlib import Path

    from src.pipeline.loaders import load_file

    for path in sorted(Path("data/samples").iterdir()):
        if path.name.startswith("."):
            continue
        raw = load_file(path)
        cleaned = clean_documents(raw)
        raw_characters = sum(len(document.page_content) for document in raw)
        cleaned_characters = sum(len(document.page_content) for document in cleaned)
        print(f"{path.name}: {len(raw)} -> {len(cleaned)} document(s), "
              f"{raw_characters} -> {cleaned_characters} characters")

    print("\n=== messy_report.pdf after cleaning")
    for document in clean_documents(load_file("data/samples/messy_report.pdf")):
        print(f"--- page {document.metadata['page']}")
        print(document.page_content)
