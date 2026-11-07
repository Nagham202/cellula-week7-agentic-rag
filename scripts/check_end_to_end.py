# upload -> ask -> follow-up -> re-upload -> delete, like a real user would
# uses the real data/qdrant and removes its test file at the end (3 llm calls)
# python -m scripts.check_end_to_end

import tempfile
from pathlib import Path

from src.pipeline.ingest import ingest_file
from src.pipeline.store import count_chunks, delete_source, list_sources
from src.retriever.retriever import retrieve, retrieve_with_details

FILE_NAME = "e2e_cafeteria_notice.txt"
VERSION_1 = "Cafeteria notice\nThe cafeteria opens at 8:00 and closes at 15:00. Lunch costs 4 dinars."
VERSION_2 = "Cafeteria notice\nThe cafeteria opens at 7:30 and closes at 16:00. Lunch costs 5 dinars."


def check(description, passed):
    print(f"[{'OK' if passed else 'FAILED'}] {description}")
    return passed


def main():
    all_passed = True
    total_before = count_chunks()

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / FILE_NAME

        path.write_text(VERSION_1)
        chunk_count = ingest_file(path)
        all_passed &= check(f"upload: {chunk_count} chunk(s) stored, file is listed", FILE_NAME in list_sources())

        evidence = retrieve("When does the cafeteria open?")
        all_passed &= check("ask: the new file is the top evidence", evidence[0]["source"] == FILE_NAME)
        all_passed &= check("ask: the evidence says 8:00", "8:00" in evidence[0]["text"])

        history = [{"role": "user", "content": "When does the cafeteria open?"},
                   {"role": "assistant", "content": "It opens at 8:00 (e2e_cafeteria_notice.txt)."}]
        details = retrieve_with_details("And how much is lunch there?", history)
        all_passed &= check(f"follow-up rewritten to: {details['search_query']!r}",
                            details["evidence"][0]["source"] == FILE_NAME)

        path.write_text(VERSION_2)
        ingest_file(path)
        texts = [item["text"] for item in retrieve(f"When does the cafeteria in {FILE_NAME} open?")
                 if item["source"] == FILE_NAME]
        all_passed &= check("re-upload: new version found (7:30)", any("7:30" in text for text in texts))
        all_passed &= check("re-upload: old version gone (no 8:00)", not any("8:00" in text for text in texts))

    delete_source(FILE_NAME)
    all_passed &= check("delete: file removed, total back to before",
                        FILE_NAME not in list_sources() and count_chunks() == total_before)

    print("\nALL CHECKS PASSED" if all_passed else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
