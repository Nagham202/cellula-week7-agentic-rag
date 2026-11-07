import pytest

from src.pipeline.loaders import SourceError, load_file

SAMPLES = "data/samples"


def test_pdf_gives_one_document_per_page_with_page_numbers():
    documents = load_file(f"{SAMPLES}/kito_manual.pdf")
    assert [document.metadata["page"] for document in documents] == [1, 2, 3]
    assert documents[0].metadata == {"source": "kito_manual.pdf", "type": "pdf", "page": 1}
    assert "Maximum load: 120 kg" in documents[0].page_content


def test_docx_keeps_tables_and_has_no_page():
    documents = load_file(f"{SAMPLES}/hr_policy.docx")
    assert len(documents) == 1
    assert documents[0].metadata == {"source": "hr_policy.docx", "type": "docx", "page": None}
    # this line comes from a word table
    assert "Parental leave | 12 weeks" in documents[0].page_content


def test_txt():
    documents = load_file(f"{SAMPLES}/nova_faq.txt")
    assert documents[0].metadata == {"source": "nova_faq.txt", "type": "txt", "page": None}
    assert "Lina Haddad" in documents[0].page_content


def test_unsupported_type_and_broken_files_give_a_clear_message(tmp_path):
    with pytest.raises(SourceError, match="Unsupported file type"):
        load_file(tmp_path / "slides.pptx")

    fake_pdf = tmp_path / "broken.pdf"
    fake_pdf.write_text("this is not really a pdf")
    with pytest.raises(SourceError, match="could not be read"):
        load_file(fake_pdf)

    latin_text = tmp_path / "old.txt"
    latin_text.write_bytes("café".encode("latin-1"))
    with pytest.raises(SourceError, match="not saved as UTF-8"):
        load_file(latin_text)


def test_empty_txt_gives_no_documents(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("   \n  ")
    assert load_file(empty) == []
