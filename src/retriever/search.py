from qdrant_client import models

import config
from src.pipeline.embeddings import embed_query, embed_sparse_query
from src.pipeline.store import create_collection, get_client


def to_evidence(point):
    evidence = dict(point.payload)
    evidence["score"] = round(point.score, 4)
    return evidence


def run_query(query, using, top_k, query_filter, prefetch=None):
    create_collection()
    response = get_client().query_points(
        collection_name=config.COLLECTION_NAME,
        query=query,
        using=using,
        prefetch=prefetch,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )
    return [to_evidence(point) for point in response.points]


def semantic_search(query, top_k=config.TOP_K, query_filter=None):
    return run_query(embed_query(query), config.DENSE_VECTOR_NAME, top_k, query_filter)


def keyword_search(query, top_k=config.TOP_K, query_filter=None):
    return run_query(embed_sparse_query(query), config.SPARSE_VECTOR_NAME, top_k, query_filter)


# RRF uses ranks, not scores, because cosine (0-1) and bm25 (0-30+) are on different scales
def hybrid_search(query, top_k=config.TOP_K, query_filter=None, candidates=config.HYBRID_CANDIDATES,
                  extra_queries=None):
    queries = [query] + (extra_queries or [])
    prefetch = []
    for one_query in queries:
        prefetch.append(models.Prefetch(query=embed_query(one_query), using=config.DENSE_VECTOR_NAME,
                                        filter=query_filter, limit=candidates))
        prefetch.append(models.Prefetch(query=embed_sparse_query(one_query), using=config.SPARSE_VECTOR_NAME,
                                        filter=query_filter, limit=candidates))
    return run_query(models.FusionQuery(fusion=models.Fusion.RRF), None, top_k, None, prefetch=prefetch)


# quick test: python -m src.retriever.search (run python -m src.pipeline.ingest first)
if __name__ == "__main__":
    questions = [
        "What does error E31 mean?",
        "What is the accuracy of BERT-base?",
        "What does Equation 12 compute?",
        "Can RAG update its knowledge without retraining the model?",
    ]
    for question in questions:
        print(f"\n=== {question}")
        for name, search in [("semantic", semantic_search), ("keyword", keyword_search), ("hybrid", hybrid_search)]:
            print(f"  {name}:")
            for evidence in search(question, top_k=3):
                preview = evidence["text"].split("\n", 1)[1][:55].replace("\n", " ")
                print(f"    {evidence['score']:7.3f}  {evidence['chunk_id']:26s} {preview}")
