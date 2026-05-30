import os
from backend.config import settings

os.environ["TAVILY_API_KEY"] = settings.tavily_api_key


def get_web_search_tool():
    from langchain_community.tools.tavily_search import TavilySearchResults
    return TavilySearchResults(
        max_results=5,
        description=(
            "Search the internet for current information, news, recent events, "
            "or any facts that may not be in training data."
        ),
    )
