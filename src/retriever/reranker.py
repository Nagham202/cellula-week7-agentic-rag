import math

from fastembed.rerank.cross_encoder import TextCrossEncoder

import config

# a dict, so the evaluation can load and compare several models
reranker_models = {}


def get_reranker(model_name):
    if model_name not in reranker_models:
        reranker_models[model_name] = TextCrossEncoder(model_name)
    return reranker_models[model_name]


def to_zero_one(raw_score):
    # sigmoid, the model gives any number (like -8 to 9) and this maps it to 0..1
    return 1 / (1 + math.exp(-raw_score))


def rerank(query, evidence_list, model_name=None):
    if not evidence_list:
        return []
    if model_name is None:
        model_name = config.RERANKER_MODEL

    texts = [evidence["text"] for evidence in evidence_list]
    raw_scores = list(get_reranker(model_name).rerank(query, texts))

    reranked = []
    for evidence, raw_score in zip(evidence_list, raw_scores):
        item = dict(evidence)
        item["score"] = round(to_zero_one(raw_score), 4)
        reranked.append(item)
    reranked.sort(key=lambda item: item["score"], reverse=True)
    return reranked
