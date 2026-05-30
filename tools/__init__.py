from tools.calculator import calculator
from tools.code_executor import python_repl
from tools.file_reader import file_reader
from tools.rag_tool import document_search
from tools.web_search import get_web_search_tool


def get_all_tools():
    tools = [
        calculator,
        python_repl,
        file_reader,
        document_search,
    ]
    try:
        tools.insert(0, get_web_search_tool())
    except Exception:
        pass  # Tavily key missing — web search disabled
    return tools
