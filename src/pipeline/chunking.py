import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

# "4 Results", "4.2 Training", "Chapter 4: Results", "Section 2.1 Models"
HEADING_PATTERN = re.compile(r"^(?:(?:Chapter|Section)\s+)?(\d{1,2}(?:\.\d{1,2})*)\.?:?\s+[A-Z]")
# appendix headings in papers: "A Implementation Details", "G Parameters"
APPENDIX_PATTERN = re.compile(r"^([A-H])\s+[A-Z]")
NAMED_HEADINGS = {"Abstract", "Introduction", "Conclusion", "Conclusions", "Acknowledgments",
                  "Acknowledgements", "Broader Impact", "References", "Bibliography", "Appendix"}
MAX_HEADING_LENGTH = 80


def read_heading(line, in_appendix=False):
    if line in NAMED_HEADINGS:
        return line, None
    # headings don't end with a full stop, sentences and list items usually do
    if len(line) > MAX_HEADING_LENGTH or line.endswith("."):
        return None
    # only after the references, before that "A Kito robot moves shelves" would match
    if in_appendix:
        match = APPENDIX_PATTERN.match(line)
        if match is not None:
            return line, match.group(1)
    match = HEADING_PATTERN.match(line)
    if match is None:
        return None
    number = match.group(1)
    chapter = number.split(".")[0]
    return line, chapter


def split_into_sections(documents):
    pieces = []
    # outside the page loop, so a section continues on the next page like in a book
    section = None
    chapter = None
    in_appendix = False

    for document in documents:
        lines = []
        for line in document.page_content.split("\n"):
            heading = read_heading(line, in_appendix)
            if heading is not None:
                if lines:
                    pieces.append(make_piece(document, lines, section, chapter))
                section, chapter = heading
                lines = []
                if section in ("References", "Bibliography"):
                    in_appendix = True
            lines.append(line)
        if lines:
            pieces.append(make_piece(document, lines, section, chapter))
    return pieces


def make_piece(document, lines, section, chapter):
    # a copy, otherwise all pieces of a page would share (and overwrite) one dict
    metadata = dict(document.metadata)
    metadata["section"] = section
    metadata["chapter"] = chapter
    return Document(page_content="\n".join(lines), metadata=metadata)


# every chunk starts with where it comes from, so the answer can cite it
def make_header(metadata):
    header = f"Source: {metadata['source']}"
    if metadata["page"] is not None:
        header += f", page {metadata['page']}"
    if metadata["section"] is not None:
        header += f", section: {metadata['section']}"
    return header


def make_chunk_id(metadata, number):
    if metadata["page"] is not None:
        return f"{metadata['source']}_p{metadata['page']}_c{number}"
    return f"{metadata['source']}_c{number}"


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    pieces = []
    for piece in splitter.split_documents(split_into_sections(documents)):
        # a heading at the end of a page gives a piece with nothing else, its text is in the next one
        if piece.page_content.strip() == piece.metadata["section"]:
            continue
        pieces.append(piece)

    chunks = []
    for number, piece in enumerate(pieces, start=1):
        chunk = dict(piece.metadata)
        chunk["chunk_id"] = make_chunk_id(piece.metadata, number)
        chunk["text"] = make_header(piece.metadata) + "\n" + piece.page_content
        chunks.append(chunk)
    return chunks


# quick test: python -m src.pipeline.chunking
if __name__ == "__main__":
    from pathlib import Path

    from src.pipeline.cleaning import clean_documents
    from src.pipeline.loaders import load_file

    for path in sorted(Path("data/samples").iterdir()):
        if path.name.startswith("."):
            continue
        chunks = chunk_documents(clean_documents(load_file(path)))
        sizes = [len(chunk["text"]) for chunk in chunks]
        sections = {chunk["section"] for chunk in chunks if chunk["section"] is not None}
        print(f"{path.name}: {len(chunks)} chunks, size {min(sizes)}-{max(sizes)} characters, "
              f"{len(sections)} sections")

    print("\n=== Two chunks of messy_report.pdf")
    chunks = chunk_documents(clean_documents(load_file("data/samples/messy_report.pdf")))
    for chunk in chunks[1:3]:
        print({key: value for key, value in chunk.items() if key != "text"})
        print(chunk["text"], "\n")

    print("=== Chunks of rag_paper.pdf in chapter 4 (first 3)")
    chunks = chunk_documents(clean_documents(load_file("data/samples/rag_paper.pdf")))
    for chunk in [chunk for chunk in chunks if chunk["chapter"] == "4"][:3]:
        print(chunk["chunk_id"], "|", chunk["section"])
