# same functions as retriever.py but with made-up evidence, for tests that shouldn't need qdrant

import config

FAKE_EVIDENCE = [
    {
        "source": "rag.pdf",
        "page": 5,
        "text": "Source: rag.pdf, page 5\nRAG allows a model to access external knowledge at query time, "
                "so its knowledge can be updated without retraining.",
        "score": 0.94,
        "chunk_id": "rag.pdf_p5_c1",
    },
    {
        "source": "rag.pdf",
        "page": 8,
        "text": "Source: rag.pdf, page 8\nA disadvantage of RAG is that answer quality depends on "
                "retrieval quality: if the wrong chunks are retrieved, the answer is wrong.",
        "score": 0.91,
        "chunk_id": "rag.pdf_p8_c3",
    },
    {
        "source": "paper_a.pdf",
        "page": 4,
        "text": "Source: paper_a.pdf, page 4\nTable 2: The CNN model reached an accuracy of 92% on the test set.",
        "score": 0.88,
        "chunk_id": "paper_a.pdf_p4_c2",
    },
    {
        "source": "paper_b.pdf",
        "page": 6,
        "text": "Source: paper_b.pdf, page 6\nOur CNN achieves 95% accuracy, outperforming previous work.",
        "score": 0.86,
        "chunk_id": "paper_b.pdf_p6_c1",
    },
    {
        "source": "paper_c.pdf",
        "page": 3,
        "text": "Source: paper_c.pdf, page 3\nThe CNN baseline obtained 89% accuracy.",
        "score": 0.83,
        "chunk_id": "paper_c.pdf_p3_c4",
    },
    {
        "source": "notes.docx",
        "page": None,
        "text": "Source: notes.docx\nFine-tuning changes the model weights, while RAG keeps the model "
                "fixed and changes the documents it reads.",
        "score": 0.80,
        "chunk_id": "notes.docx_c2",
    },
    {
        "source": "paper_a.pdf",
        "page": 7,
        "text": "Source: paper_a.pdf, page 7\nThe CNN has 1.2 million parameters and needs 0.6 GFLOPs per image.",
        "score": 0.75,
        "chunk_id": "paper_a.pdf_p7_c1",
    },
]


def retrieve(question, chat_history=None, top_k=config.TOP_K, filters=None):
    return FAKE_EVIDENCE[:top_k]


def retrieve_more(query, already_seen_ids=None, top_k=4):
    if already_seen_ids is None:
        already_seen_ids = []

    new_items = []
    for item in FAKE_EVIDENCE:
        if item["chunk_id"] not in already_seen_ids:
            new_items.append(item)
    return new_items[:top_k]


# quick test: python -m src.retriever.fake_retriever
if __name__ == "__main__":
    first = retrieve("What is the average CNN accuracy?")
    print("retrieve() returned", len(first), "items:")
    for item in first:
        print(" ", item["chunk_id"], item["score"])

    seen = [item["chunk_id"] for item in first]
    more = retrieve_more("CNN computational complexity", already_seen_ids=seen)
    print("retrieve_more() returned", len(more), "new items:")
    for item in more:
        print(" ", item["chunk_id"], item["score"])
