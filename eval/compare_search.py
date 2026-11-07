# compares the search versions on eval/questions.json
# hit@k = share of questions with a right chunk in the top k
# MRR = average of 1/rank of the first right chunk (0 if not found)
# python -m eval.compare_search

import json
import time
from pathlib import Path

import config
from src.retriever.query_rewriter import rewrite_query
from src.retriever.retriever import rerank_and_select
from src.retriever.search import hybrid_search, keyword_search, semantic_search

TOP_K = 5
RESULTS_DIR = Path("eval/results")
REWRITES_FILE = RESULTS_DIR / "rewrites.json"
# stays under groq's per-minute limit, so no call falls back to a different model
SECONDS_BETWEEN_LLM_CALLS = 2
VERSIONS = ["semantic", "keyword", "hybrid", "hybrid+rewrite", "hybrid+rewrite+alts", "+rerank+select"]


def load_rewrites(questions):
    saved = {}
    if REWRITES_FILE.exists():
        saved = json.loads(REWRITES_FILE.read_text())

    for question in questions:
        if question["question"] in saved:
            continue
        saved[question["question"]] = rewrite_query(question["question"], question.get("history"))
        time.sleep(SECONDS_BETWEEN_LLM_CALLS)

    RESULTS_DIR.mkdir(exist_ok=True)
    REWRITES_FILE.write_text(json.dumps(saved, indent=2))
    return saved


def search_all_versions(question, rewrite):
    text = question["question"]
    original = [text] if rewrite["query"] != text else []
    # same steps as retrieve()
    candidates = hybrid_search(rewrite["query"], top_k=config.RERANK_CANDIDATES,
                               extra_queries=rewrite["alternatives"] + original)
    return {
        "semantic": semantic_search(text, top_k=TOP_K),
        "keyword": keyword_search(text, top_k=TOP_K),
        "hybrid": hybrid_search(text, top_k=TOP_K),
        "hybrid+rewrite": hybrid_search(rewrite["query"], top_k=TOP_K, extra_queries=original),
        "hybrid+rewrite+alts": candidates[:TOP_K],
        "+rerank+select": rerank_and_select(rewrite["query"], candidates, TOP_K, {}),
    }


def first_right_rank(results, question):
    for rank, evidence in enumerate(results, start=1):
        if evidence["source"] == question["source"] and evidence["page"] in question["pages"]:
            return rank
    return None


def score(ranks):
    count = len(ranks)
    return {
        "hit@1": sum(1 for rank in ranks if rank is not None and rank <= 1) / count,
        "hit@3": sum(1 for rank in ranks if rank is not None and rank <= 3) / count,
        "hit@5": sum(1 for rank in ranks if rank is not None and rank <= 5) / count,
        "MRR": sum(1 / rank for rank in ranks if rank is not None) / count,
    }


def main():
    questions = json.loads(Path("eval/questions.json").read_text())
    rewrites = load_rewrites(questions)

    ranks = {version: [] for version in VERSIONS}
    detail = ["| Question | Type | " + " | ".join(VERSIONS) + " |", "|---|---|" + "---|" * len(VERSIONS)]
    for question in questions:
        results = search_all_versions(question, rewrites[question["question"]])
        row = []
        for version in VERSIONS:
            rank = first_right_rank(results[version], question)
            ranks[version].append(rank)
            row.append(str(rank) if rank is not None else "-")
        detail.append(f"| {question['question']} | {question['type']} | " + " | ".join(row) + " |")

    summary = ["| Version | Questions | hit@1 | hit@3 | hit@5 | MRR |", "|---|---|---|---|---|---|"]
    for question_type in ["all", "meaning", "exact", "followup"]:
        for version in VERSIONS:
            chosen = [rank for rank, question in zip(ranks[version], questions)
                      if question_type == "all" or question["type"] == question_type]
            result = score(chosen)
            summary.append(f"| {version} | {question_type} ({len(chosen)}) | " +
                           " | ".join(f"{result[key]:.2f}" for key in ["hit@1", "hit@3", "hit@5", "MRR"]) + " |")

    failed_rewrites = [text for text, rewrite in rewrites.items() if not rewrite["rewritten"]]
    report = ("## Search comparison\n\n" + "\n".join(summary) +
              f"\n\nRewrites that fell back to the original question: {len(failed_rewrites)}\n" +
              "\n### Rank of the first right chunk (- = not in top 5)\n\n" + "\n".join(detail) + "\n")
    print(report)
    (RESULTS_DIR / "search_comparison.md").write_text(report)
    print(f"Saved {RESULTS_DIR / 'search_comparison.md'} and {REWRITES_FILE}")


if __name__ == "__main__":
    main()
