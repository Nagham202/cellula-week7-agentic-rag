import atexit
import uuid

from qdrant_client import QdrantClient, models

import config
from src.pipeline.embeddings import embed_sparse_texts, embed_texts

# local mode locks the folder, so the whole program shares one client
client = None


def get_client():
    global client
    if client is None:
        try:
            client = QdrantClient(path=config.QDRANT_PATH)
        except RuntimeError as error:
            raise RuntimeError(f"Qdrant could not open {config.QDRANT_PATH}. Another program is probably "
                               f"using it (the Streamlit app or another script). Close it and try again.") from error
        # without this qdrant prints an error while python shuts down
        atexit.register(client.close)
    return client


def create_collection():
    qdrant = get_client()
    if qdrant.collection_exists(config.COLLECTION_NAME):
        return
    # measured instead of hard-coding 384, so changing the model can't break it
    vector_size = len(embed_texts(["size check"])[0])
    qdrant.create_collection(
        collection_name=config.COLLECTION_NAME,
        vectors_config={
            config.DENSE_VECTOR_NAME: models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        },
        # qdrant works out how rare each word is, rare words count more
        sparse_vectors_config={
            config.SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF),
        },
    )


def point_id(chunk_id):
    # qdrant ids must be a number or a uuid, uuid5 gives the same one for the same chunk_id
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def match(key, value):
    return models.FieldCondition(key=key, match=models.MatchValue(value=value))


def add_chunks(chunks):
    create_collection()
    texts = [chunk["text"] for chunk in chunks]
    dense_vectors = embed_texts(texts)
    sparse_vectors = embed_sparse_texts(texts)

    points = []
    for chunk, dense_vector, sparse_vector in zip(chunks, dense_vectors, sparse_vectors):
        points.append(models.PointStruct(
            id=point_id(chunk["chunk_id"]),
            vector={config.DENSE_VECTOR_NAME: dense_vector, config.SPARSE_VECTOR_NAME: sparse_vector},
            payload=chunk,
        ))

    qdrant = get_client()
    # add the new version first and delete leftovers after, so a failure never loses the old version
    qdrant.upsert(collection_name=config.COLLECTION_NAME, points=points)

    new_chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    leftovers = models.Filter(
        must=[match("source", chunks[0]["source"])],
        must_not=[models.FieldCondition(key="chunk_id", match=models.MatchAny(any=new_chunk_ids))],
    )
    qdrant.delete(collection_name=config.COLLECTION_NAME, points_selector=models.FilterSelector(filter=leftovers))
    return len(points)


def delete_source(source):
    create_collection()
    get_client().delete(
        collection_name=config.COLLECTION_NAME,
        points_selector=models.FilterSelector(filter=models.Filter(must=[match("source", source)])),
    )


def list_sources():
    create_collection()
    sources = set()
    # scroll reads page by page, offset is None when there's nothing left
    offset = None
    while True:
        points, offset = get_client().scroll(
            collection_name=config.COLLECTION_NAME,
            with_payload=["source"],
            with_vectors=False,
            limit=256,
            offset=offset,
        )
        for point in points:
            sources.add(point.payload["source"])
        if offset is None:
            break
    return sorted(sources)


def count_chunks(source=None):
    create_collection()
    count_filter = None
    if source is not None:
        count_filter = models.Filter(must=[match("source", source)])
    return get_client().count(collection_name=config.COLLECTION_NAME, count_filter=count_filter).count
