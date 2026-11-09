
import statistics
from langchain.tools import tool


def calculate_mean(numbers):
    return statistics.mean(numbers)


def calculate_median(numbers):
    return statistics.median(numbers)


def calculate_range(numbers):
    return max(numbers) - min(numbers)


def calculate_std(numbers):
    if len(numbers) < 2:
        return 0.0

    return statistics.stdev(numbers)


def analyze_data(numbers):

    if not numbers:
        raise ValueError("Please provide numbers for analysis")

    return {
        "count": len(numbers),
        "mean": calculate_mean(numbers),
        "median": calculate_median(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
        "range": calculate_range(numbers),
        "standard_deviation": calculate_std(numbers)
    }


def rank_models(models):

    return sorted(
        models.items(),
        key=lambda item: item[1],
        reverse=True
    )


def detect_trend(numbers):

    if len(numbers) < 2:
        return "Not enough data"

    if all(numbers[i] <= numbers[i + 1]
           for i in range(len(numbers) - 1)):
        return "Increasing"

    if all(numbers[i] >= numbers[i + 1]
           for i in range(len(numbers) - 1)):
        return "Decreasing"

    return "Fluctuating"


@tool
def data_analysis_tool(
    numbers: list[float],
    models: dict[str,float] = None
    )-> dict:
    """
    Analyze a list of numerical values.

    Calculates count, mean, median, minimum, maximum,
    range, and standard deviation.
    """

    result = analyze_data(numbers)

    result["trend"] = detect_trend(numbers)

    if models:
        result["ranking"] = rank_models(models)

    return result
