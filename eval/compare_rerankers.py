# compares reranker models on the same 20 candidates per question (quality and speed)
# python -m eval.compare_rerankers  (run compare_search first, it saves the rewrites)

import json
import time
from pathlib import Path

import config
from eval.compare_search import REWRITES_FILE, RESULTS_DIR, TOP_K, first_right_rank, score
from src.retriever.reranker import get_reranker, rerank
from src.retriever.search import hybrid_search

MODELS = ["Xenova/ms-marco-MiniLM-L-6-v2", "Xenova/ms-marco-MiniLM-L-12-v2", "BAAI/bge-reranker-base"]


def main():
    questions = json.loads(Path("eval/questions.json").read_text())
    rewrites = json.loads(REWRITES_FILE.read_text())

    candidates = []
    for question in questions:
        rewrite = rewrites[question["question"]]
        original = [question["question"]] if rewrite["query"] != question["question"] else []
        found = hybrid_search(rewrite["query"], top_k=config.RERANK_CANDIDATES,
                              extra_queries=rewrite["alternatives"] + original)
        candidates.append((rewrite["query"], found))

    ranks = {"no reranker": [first_right_rank(found[:TOP_K], question)
                             for (_, found), question in zip(candidates, questions)]}
    seconds = {"no reranker": 0.0}
    for model_name in MODELS:
        # loaded before the timer starts, so only the reranking is timed
        get_reranker(model_name)
        start = time.time()
        ranks[model_name] = []
        for (query, found), question in zip(candidates, questions):
            ranks[model_name].append(first_right_rank(rerank(query, found, model_name)[:TOP_K], question))
        seconds[model_name] = (time.time() - start) / len(questions)

    lines = ["| Reranker | Questions | hit@1 | hit@3 | hit@5 | MRR | ms per question |", "|---|---|---|---|---|---|---|"]
    for question_type in ["all", "meaning", "exact", "followup"]:
        for name, model_ranks in ranks.items():
            chosen = [rank for rank, question in zip(model_ranks, questions)
                      if question_type == "all" or question["type"] == question_type]
            result = score(chosen)
            lines.append(f"| {name} | {question_type} ({len(chosen)}) | " +
                         " | ".join(f"{result[key]:.2f}" for key in ["hit@1", "hit@3", "hit@5", "MRR"]) +
                         f" | {seconds[name] * 1000:.0f} |")

    detail = ["| Question | " + " | ".join(ranks) + " |", "|---|" + "---|" * len(ranks)]
    for number, question in enumerate(questions):
        row = [str(ranks[name][number]) if ranks[name][number] is not None else "-" for name in ranks]
        detail.append(f"| {question['question']} | " + " | ".join(row) + " |")

    report = (f"## Reranker comparison ({config.RERANK_CANDIDATES} candidates, top {TOP_K})\n\n" +
              "\n".join(lines) + "\n\n### Rank of the first right chunk\n\n" + "\n".join(detail) + "\n")
    print(report)
    (RESULTS_DIR / "reranker_comparison.md").write_text(report)


if __name__ == "__main__":
    main()
