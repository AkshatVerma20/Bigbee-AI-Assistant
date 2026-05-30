import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List

from backend.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_COLLECTION_NAME = "document_store"

_embeddings = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model="text-embedding-3-small",
        )
    return _embeddings


def _get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=_COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
        client_settings=ChromaSettings(anonymized_telemetry=False),
    )


def index_document(chunks: List[Document], source: str = "unknown"):
    vs = _get_vectorstore()
    for chunk in chunks:
        chunk.metadata["source"] = source
    vs.add_documents(chunks)
    logger.info(f"Indexed {len(chunks)} chunks from '{source}'")


def similarity_search(query: str, top_k: int = 4, source_filter: str = None) -> List[Document]:
    vs = _get_vectorstore()
    where = {"source": source_filter} if source_filter else None
    try:
        return vs.similarity_search(query, k=top_k, filter=where)
    except Exception as e:
        logger.warning(f"Vector search error: {e}")
        return []


def list_indexed_sources() -> List[str]:
    vs = _get_vectorstore()
    try:
        data = vs._collection.get(include=["metadatas"])
        return sorted({m.get("source", "") for m in data["metadatas"] if m})
    except Exception:
        return []
