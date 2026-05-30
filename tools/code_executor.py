from langchain_core.tools import tool
import subprocess
import sys
import tempfile
import os


@tool
def python_repl(code: str) -> str:
    """Execute Python code and return the output.
    Use for data analysis, computations, file processing, or testing logic.
    The code runs in an isolated subprocess with a 15-second timeout.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            [sys.executable, fname],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = (result.stdout + result.stderr).strip()
        return output[:3000] if output else "Code executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (15s limit)."
    except Exception as e:
        return f"Error running code: {e}"
    finally:
        os.unlink(fname)
