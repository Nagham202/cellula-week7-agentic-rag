
import re
from langchain.tools import tool


def extract_metrics(text):
    """
    Extract percentage metrics from document text.
    Supports formats such as:
    Accuracy: 92%
    92% accuracy
    """

    metrics = {}

    patterns = [
        r"([a-zA-Z][a-zA-Z _-]*?)\s*[:=]\s*(\d+(?:\.\d+)?)\s*%",
        r"(\d+(?:\.\d+)?)\s*%\s*([a-zA-Z][a-zA-Z _-]*)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            if pattern == patterns[0]:
                name = match[0].strip().lower()
                value = float(match[1])

            else:
                value = float(match[0])
                name = match[1].strip().lower()

            metrics[name] = value

    return metrics


def compare_metrics(metrics_a, metrics_b):

    comparisons = []

    common_metrics = set(metrics_a).intersection(metrics_b)

    for metric in sorted(common_metrics):

        value_a = metrics_a[metric]
        value_b = metrics_b[metric]

        if value_a > value_b:
            higher = "Document A"

        elif value_b > value_a:
            higher = "Document B"

        else:
            higher = "Equal"

        comparisons.append({
            "metric": metric,
            "document_a_value": value_a,
            "document_b_value": value_b,
            "higher_value": higher
        })

    return comparisons


def compare_documents(document_a, document_b):

    metrics_a = extract_metrics(document_a["text"])
    metrics_b = extract_metrics(document_b["text"])

    # Remove metric names and percentages before text comparison
    words_a = clean_comparison_text(
        document_a["text"],
        metrics_a
    )

    words_b = clean_comparison_text(
        document_b["text"],
        metrics_b
    )

    return {
        "document_a": document_a["source"],
        "document_b": document_b["source"],

        "similarities": sorted(words_a.intersection(words_b)),

        "differences": {
            "document_a_only": sorted(words_a - words_b),
            "document_b_only": sorted(words_b - words_a)
        },

        "metric_comparisons": compare_metrics(
            metrics_a,
            metrics_b
        ),

        "sources": {
            "document_a_page": document_a.get("page"),
            "document_b_page": document_b.get("page")
        }
    }

def clean_comparison_text(text, metrics):
    text = text.lower()

    text = re.sub(r"\d+(?:\.\d+)?\s*%", "", text)

    for metric in metrics:
        text = re.sub(
            rf"\b{re.escape(metric)}\b",
            "",
            text
        )

    text = re.sub(r"[^\w\s]", " ", text)

    return set(text.split())

@tool
def document_comparison_tool(
    document_a_text: str,
    document_a_source: str,
    document_b_text: str,
    document_b_source: str,
    document_a_page: int = 0,
    document_b_page: int = 0
) -> dict:
    """
    Compare two documents.

    Identifies common and unique words, extracts matching
    percentage metrics, compares their numerical values,
    and preserves document source and page information.
    """

    document_a = {
        "text": document_a_text,
        "source": document_a_source,
        "page": document_a_page or None
    }

    document_b = {
        "text": document_b_text,
        "source": document_b_source,
        "page": document_b_page or None
    }

    return compare_documents(document_a, document_b)
