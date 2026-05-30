from langchain_core.tools import tool
import math


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely.
    Input must be a valid Python math expression string.
    Examples: '2 ** 10', 'sqrt(144)', '(3 + 5) * 2'
    """
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"
