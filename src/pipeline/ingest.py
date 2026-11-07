from pathlib import Path

from src.pipeline.chunking import chunk_documents
from src.pipeline.cleaning import clean_documents
from src.pipeline.loaders import SourceError, load_file
from src.pipeline.store import add_chunks


def ingest_file(path):
    chunks = chunk_documents(clean_documents(load_file(path)))
    if not chunks:
        raise SourceError(f"No text could be found in {Path(path).name}. It may be a scanned PDF (only images).")
    return add_chunks(chunks)


# quick test: python -m src.pipeline.ingest
if __name__ == "__main__":
    import time

    from src.pipeline.store import count_chunks

    for path in sorted(Path("data/samples").iterdir()):
        if path.name.startswith("."):
            continue
        start = time.time()
        chunk_count = ingest_file(path)
        print(f"{path.name}: {chunk_count} chunks in {time.time() - start:.1f} s")
    print(f"Total chunks in Qdrant: {count_chunks()}")

    # uploading the same file again should replace its chunks, not add copies
    ingest_file("data/samples/messy_report.pdf")
    print(f"After uploading messy_report.pdf again: {count_chunks()} chunks "
          f"({count_chunks('messy_report.pdf')} from messy_report.pdf)")
