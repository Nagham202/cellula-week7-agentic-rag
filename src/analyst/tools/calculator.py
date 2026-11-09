from langchain.tools import tool
from typing import Literal

def add(a,b):
    return a + b

def subtract(a,b):
    return a - b

def multiply(a,b):
    return a * b

def divide(a,b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def calculate_average(numbers):
    if not numbers:
        raise ValueError("The list of numbers is empty.")
    return sum(numbers)/len(numbers)

def calculate_percentage(part, whole):
    if whole == 0:
        raise ValueError("The whole cannot be zero.")
    return (part / whole) * 100

def calculate_ratio(a, b):
    if b == 0:
        raise ValueError("Cannot calculate ratio with zero denominator.")
    return a/b

def calculate(operation, numbers):

    if operation == 'add':
        return sum(numbers)

    elif operation == 'subtract':
        if len(numbers) < 2 :
            raise ValueError("subtraction requires at least two numbers.")

        result = numbers[0]

        for number in numbers[1:]:
            result -= number

        return result

    elif operation == 'multiply':
        if not numbers:
            raise ValueError("Provide at least one number for multiplication.")

        result = 1

        for number in numbers:
            result *=number

        return result

    elif operation == 'divide':
        if len(numbers) != 2:
            raise ValueError("division requires exactly two numbers.")

        return divide(numbers[0], numbers[1])

    elif operation == 'average':
        return calculate_average(numbers)

    elif operation == "percentage":
            if len(numbers) != 2:
                raise ValueError("Percentage calculation requires exactly two numbers.")
            return calculate_percentage(numbers[0], numbers[1])

    elif operation == "ratio":
            if len(numbers) != 2:
                raise ValueError("Ratio calculation requires exactly two numbers.")
            return calculate_ratio(numbers[0], numbers[1])

    else:
        raise ValueError(f"Unsupported operation: {operation}")


@tool
def calculator_tool(operation: Literal[
    "add",
    "subtract",
    "multiply",
    "divide",
    "average",
    "percentage",
    "ratio"
],
numbers: list[float]
) -> float:
    """
    Perform mathematical calculations.

    Supported operations:
    - add: Add multiple numbers.
    - subtract: Subtract numbers sequentially.
    - multiply: Multiply multiple numbers.
    - divide: Divide two numbers.
    - average: Calculate the average.
    - percentage: Calculate what percentage the first number
      represents of the second number.
    - ratio: Divide the first number by the second number.
    """

    return calculate(operation, numbers)
