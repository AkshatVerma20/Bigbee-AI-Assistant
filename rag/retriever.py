from rag.vectorstore import similarity_search
from langchain_core.documents import Document
from typing import List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


def retrieve_context(query: str, top_k: int = 4) -> Tuple[str, List[str]]:
    docs = similarity_search(query, top_k=top_k)
    if not docs:
        return "", []

    sources = list({d.metadata.get("source", "unknown") for d in docs})
    context_parts = []
    for i, doc in enumerate(docs, 1):
        src = doc.metadata.get("source", "unknown")
        context_parts.append(f"[Excerpt {i} — {src}]\n{doc.page_content}")

    return "\n\n---\n\n".join(context_parts), sources
