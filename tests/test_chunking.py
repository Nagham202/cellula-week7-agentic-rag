from langchain_core.documents import Document

from src.pipeline.chunking import chunk_documents, read_heading


def make_pdf_pages(page_texts):
    return [Document(page_content=text, metadata={"source": "paper.pdf", "type": "pdf", "page": number})
            for number, text in enumerate(page_texts, start=1)]


def test_read_heading_finds_numbered_headings():
    assert read_heading("4 Results") == ("4 Results", "4")
    assert read_heading("4.2 Abstractive Question Answering") == ("4.2 Abstractive Question Answering", "4")
    assert read_heading("Chapter 3: Methods") == ("Chapter 3: Methods", "3")


def test_read_heading_ignores_normal_lines():
    assert read_heading("120 kg is the maximum load") is None
    assert read_heading("2019 was the year we started") is None
    assert read_heading("2,000 questions were used") is None
    assert read_heading("1. Install the package.") is None
    assert read_heading("Results are shown below") is None


def test_named_and_appendix_headings():
    assert read_heading("References") == ("References", None)
    assert read_heading("G Parameters", in_appendix=True) == ("G Parameters", "G")
    # before the references, a line like this is a normal sentence
    assert read_heading("A Kito robot moves shelves") is None


def test_section_continues_on_next_page_and_heading_only_piece_is_dropped():
    pages = make_pdf_pages([
        "Intro text on page one.\n2 Methods",
        "We trained the model for ten epochs.",
    ])
    chunks = chunk_documents(pages)
    assert len(chunks) == 2
    assert chunks[0]["section"] is None
    assert chunks[1]["section"] == "2 Methods"
    assert chunks[1]["chapter"] == "2"
    assert chunks[1]["page"] == 2
    assert chunks[1]["text"].startswith("Source: paper.pdf, page 2, section: 2 Methods\n")


def test_every_chunk_has_the_agreed_keys_and_unique_ids():
    word_file = [Document(page_content="Some text. " * 200, metadata={"source": "a.docx", "type": "docx", "page": None})]
    chunks = chunk_documents(word_file)
    assert len(chunks) > 1
    for chunk in chunks:
        assert set(chunk) == {"source", "type", "page", "section", "chapter", "chunk_id", "text"}
        assert chunk["text"].startswith("Source: a.docx\n")
    ids = [chunk["chunk_id"] for chunk in chunks]
    assert ids[0] == "a.docx_c1"
    assert len(ids) == len(set(ids))
