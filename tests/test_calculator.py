
from src.analyst.tools.calculator import (
    calculate,
    calculate_percentage,
    calculate_ratio
)

print("Addition:", calculate("add", [10, 20, 30]))

print("Subtraction:", calculate("subtract", [100, 20, 10]))

print("Multiplication:", calculate("multiply", [2, 3, 4]))

print("Division:", calculate("divide", [100, 5]))

print("Average:", calculate("average", [90, 80, 100]))

print("Percentage:", calculate_percentage(25, 100))

print("Ratio:", calculate_ratio(10, 5))
