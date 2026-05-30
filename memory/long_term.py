import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from typing import List
import uuid
from datetime import datetime

from backend.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LongTermMemory:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model="text-embedding-3-small",
        )
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=f"user_memory_{user_id}",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Long-term memory initialized for user: {user_id}")

    def store(self, fact: str, metadata: dict = None):
        embedding = self.embeddings.embed_query(fact)
        doc_id = str(uuid.uuid4())
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[fact],
            metadatas=[{
                "user_id": self.user_id,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {}),
            }],
        )
        logger.debug(f"Stored memory: {fact[:60]}...")

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        if self.collection.count() == 0:
            return []
        embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, self.collection.count()),
        )
        return results["documents"][0] if results["documents"] else []

    def clear(self):
        self.client.delete_collection(f"user_memory_{self.user_id}")
        self.collection = self.client.get_or_create_collection(
            name=f"user_memory_{self.user_id}",
        )
