from langchain_core.documents import Document

from src.pipeline.cleaning import clean_documents, join_broken_lines, normalize_text


def make_pdf_pages(page_texts):
    return [Document(page_content=text, metadata={"source": "test.pdf", "type": "pdf", "page": number})
            for number, text in enumerate(page_texts, start=1)]


def test_normalize_fixes_characters_and_spaces():
    text = "The   ﬁnal score\n\n\n\nNext paragraph"
    assert normalize_text(text) == "The final score\n\nNext paragraph"


def test_join_removes_hyphen_and_joins_sentences():
    assert join_broken_lines("the docu-\nments") == "the documents"
    assert join_broken_lines("it can be updated\nwithout retraining") == "it can be updated without retraining"


def test_join_keeps_table_rows_headings_and_lines_after_colon():
    text = "Model | Accuracy\nBERT-base | 88.4%\n2. Results\nThe score uses Equation 12:\nscore = 0.7 * accuracy"
    assert join_broken_lines(text) == text


def test_repeated_header_and_page_numbers_are_removed():
    pages = make_pdf_pages([
        "My Report\nPage 1 of 3\nFirst page text.",
        "My Report\nPage 2 of 3\nSecond page text.",
        "My Report\nPage 3 of 3\nThird page text.",
    ])
    cleaned = clean_documents(pages)
    assert [document.page_content for document in cleaned] == [
        "First page text.", "Second page text.", "Third page text."]


def test_page_numbers_with_one_and_two_digits_are_removed():
    # "9" and "12" have to count as the same footer
    words = ["Apples.", "Bananas.", "Cherries.", "Dates.", "Figs."]
    pages = make_pdf_pages([f"{word}\n{number}" for word, number in zip(words, range(8, 13))])
    cleaned = clean_documents(pages)
    assert [document.page_content for document in cleaned] == words


def test_repeated_line_in_the_middle_of_a_page_is_kept():
    pages = make_pdf_pages([
        "Header\nIntro\nSee Table 1\nMore text\nEnd one",
        "Header\nBody\nSee Table 1\nMore text\nEnd two",
        "Header\nOutro\nSee Table 1\nMore text\nEnd three",
    ])
    for document in clean_documents(pages):
        assert "See Table 1" in document.page_content
        assert "Header" not in document.page_content


def test_page_with_only_header_and_footer_is_dropped_and_page_numbers_kept():
    pages = make_pdf_pages([
        "My Report\nPage 1 of 3\nReal text.",
        "My Report\nPage 2 of 3",
        "My Report\nPage 3 of 3\nMore real text.",
    ])
    cleaned = clean_documents(pages)
    assert [document.metadata["page"] for document in cleaned] == [1, 3]


def test_short_pdf_and_docx_keep_their_first_line():
    two_pages = make_pdf_pages(["Title\nText one.", "Title\nText two."])
    assert all(document.page_content.startswith("Title") for document in clean_documents(two_pages))

    word_file = [Document(page_content="Title\nSome text.", metadata={"source": "a.docx", "type": "docx", "page": None})]
    assert clean_documents(word_file)[0].page_content == "Title\nSome text."
