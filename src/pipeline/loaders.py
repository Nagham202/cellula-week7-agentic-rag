from pathlib import Path

import docx
from langchain_core.documents import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]


# our own error type, so the app can show our message instead of a library error
class SourceError(ValueError):
    pass


# one document per page so the answer can say which page
def load_pdf(path, source_name):
    reader = PdfReader(path)
    documents = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        # scanned pages have no text
        if not text.strip():
            continue

        metadata = {"source": source_name, "type": "pdf", "page": page_number}
        documents.append(Document(page_content=text, metadata=metadata))
    return documents


# word doesn't store pages, so the whole file is one document
def load_docx(path, source_name):
    word_file = docx.Document(path)
    parts = [paragraph.text for paragraph in word_file.paragraphs if paragraph.text.strip()]

    # tables aren't part of the paragraphs, without this their text is lost
    for table in word_file.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))

    text = "\n".join(parts)
    if not text.strip():
        return []
    metadata = {"source": source_name, "type": "docx", "page": None}
    return [Document(page_content=text, metadata=metadata)]


def load_txt(path, source_name):
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    metadata = {"source": source_name, "type": "txt", "page": None}
    return [Document(page_content=text, metadata=metadata)]


def load_file(path):
    path = Path(path)
    source_name = path.name
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise SourceError(f"Unsupported file type: {extension}. Please upload a PDF, DOCX or TXT file.")

    try:
        if extension == ".pdf":
            return load_pdf(path, source_name)
        if extension == ".docx":
            return load_docx(path, source_name)
        return load_txt(path, source_name)
    except UnicodeDecodeError as error:
        raise SourceError(f"{source_name} is not saved as UTF-8 text. Save it as UTF-8 and upload it again.") from error
    # every library fails differently on a broken file, the user just gets one clear message
    except Exception as error:
        raise SourceError(f"{source_name} could not be read. The file may be damaged, "
                          f"or not really a {extension} file.") from error


# quick test: python -m src.pipeline.loaders
if __name__ == "__main__":
    for path in sorted(Path("data/samples").iterdir()):
        if path.name.startswith("."):
            continue
        documents = load_file(path)
        total_characters = sum(len(doc.page_content) for doc in documents)
        print(f"{path.name}: {len(documents)} document(s), {total_characters} characters")
        print(f"  metadata: {documents[0].metadata}")
        print(f"  start: {documents[0].page_content[:100]!r}\n")
