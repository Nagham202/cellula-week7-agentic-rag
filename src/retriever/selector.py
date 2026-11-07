import config
from src.pipeline.embeddings import embed_texts


def cosine_similarity(vector_a, vector_b):
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    length_a = sum(a * a for a in vector_a) ** 0.5
    length_b = sum(b * b for b in vector_b) ** 0.5
    return dot / (length_a * length_b)


def order_for_coverage(evidence_list, must_cover_sources):
    # the best chunk of each named file goes first, so a comparison gets every side
    first = []
    for source in must_cover_sources or []:
        for evidence in evidence_list:
            if evidence["source"] == source:
                first.append(evidence)
                break
    rest = [evidence for evidence in evidence_list if evidence not in first]
    return first + rest


def select_context(evidence_list, top_k=config.TOP_K, must_cover_sources=None,
                   max_characters=config.MAX_CONTEXT_CHARACTERS, max_similarity=config.DUPLICATE_SIMILARITY):
    top_k = min(top_k, config.MAX_EVIDENCE)
    ordered = order_for_coverage(evidence_list, must_cover_sources)
    vectors = embed_texts([evidence["text"] for evidence in ordered])

    chosen = []
    chosen_vectors = []
    used_characters = 0
    for evidence, vector in zip(ordered, vectors):
        if len(chosen) == top_k:
            break
        # almost the same text as one we already have
        if any(cosine_similarity(vector, other) > max_similarity for other in chosen_vectors):
            continue
        # over the size budget, but the first chunk is always kept
        if chosen and used_characters + len(evidence["text"]) > max_characters:
            continue
        chosen.append(evidence)
        chosen_vectors.append(vector)
        used_characters += len(evidence["text"])

    # the coverage step can move a weaker chunk up, so sort again
    chosen.sort(key=lambda item: item["score"], reverse=True)
    return chosen
