from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client import models

import config

# loading takes a few seconds (and a download the first time), so each model is loaded once and reused
dense_model = None
sparse_model = None


def get_dense_model():
    global dense_model
    if dense_model is None:
        dense_model = TextEmbedding(config.DENSE_MODEL)
    return dense_model


def get_sparse_model():
    global sparse_model
    if sparse_model is None:
        sparse_model = SparseTextEmbedding(config.SPARSE_MODEL)
    return sparse_model


def embed_texts(texts):
    # fastembed gives numpy arrays, qdrant wants normal lists
    return [vector.tolist() for vector in get_dense_model().embed(texts)]


def embed_query(query):
    return embed_texts([config.DENSE_QUERY_PREFIX + query])[0]


def to_sparse_vector(embedding):
    return models.SparseVector(indices=embedding.indices.tolist(), values=embedding.values.tolist())


def embed_sparse_texts(texts):
    return [to_sparse_vector(embedding) for embedding in get_sparse_model().embed(texts)]


def embed_sparse_query(query):
    # query_embed, not embed: in a question every word just counts once
    return to_sparse_vector(next(iter(get_sparse_model().query_embed(query))))
