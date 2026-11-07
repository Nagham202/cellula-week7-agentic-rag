import config
from src.pipeline import store


def make_chunks(source, count):
    return [{"source": source, "type": "txt", "page": None, "section": None, "chapter": None,
             "chunk_id": f"{source}_c{number}", "text": f"Source: {source}\nThis is chunk number {number}."}
            for number in range(1, count + 1)]


def use_temporary_database(tmp_path, monkeypatch):
    # a temporary folder, so the real data/qdrant is never touched
    monkeypatch.setattr(config, "QDRANT_PATH", str(tmp_path / "qdrant"))
    monkeypatch.setattr(store, "client", None)


def test_point_id_is_always_the_same_for_the_same_chunk():
    assert store.point_id("a.pdf_p1_c1") == store.point_id("a.pdf_p1_c1")
    assert store.point_id("a.pdf_p1_c1") != store.point_id("a.pdf_p1_c2")


def test_reupload_replaces_old_chunks_and_keeps_other_files(tmp_path, monkeypatch):
    use_temporary_database(tmp_path, monkeypatch)
    store.add_chunks(make_chunks("a.txt", 5))
    store.add_chunks(make_chunks("b.txt", 2))

    # the new version is shorter, chunks 4 and 5 have to go
    store.add_chunks(make_chunks("a.txt", 3))
    assert store.count_chunks("a.txt") == 3
    assert store.count_chunks("b.txt") == 2


def test_delete_source(tmp_path, monkeypatch):
    use_temporary_database(tmp_path, monkeypatch)
    store.add_chunks(make_chunks("a.txt", 3))
    store.add_chunks(make_chunks("b.txt", 2))
    store.delete_source("a.txt")
    assert store.count_chunks() == 2
