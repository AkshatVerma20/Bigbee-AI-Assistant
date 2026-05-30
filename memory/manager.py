from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, BaseMessage
from typing import List

from backend.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    def __init__(self, user_id: str = "default", session_id: str = "default"):
        self.user_id = user_id
        self.session_id = session_id
        self.short_term = ShortTermMemory(max_messages=20)
        self.long_term = LongTermMemory(user_id=user_id)
        self._llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.openai_api_key,
        )

    def add_exchange(self, user_message: str, ai_response: str):
        self.short_term.add_user_message(user_message)
        self.short_term.add_ai_message(ai_response)
        self._extract_and_store(user_message, ai_response)

    def _extract_and_store(self, user_msg: str, ai_msg: str):
        try:
            prompt = (
                "Extract 0-3 important facts about the USER from this exchange.\n"
                "Facts should be personal preferences, goals, background, or explicit requests to remember.\n"
                "Return ONLY a newline-separated list. If nothing memorable, return 'NONE'.\n\n"
                f"User: {user_msg}\nAssistant: {ai_msg}"
            )
            response = self._llm.invoke([SystemMessage(content=prompt)])
            facts = response.content.strip()
            if facts and facts.upper() != "NONE":
                for fact in facts.split("\n"):
                    fact = fact.strip().lstrip("-•123456789. ")
                    if len(fact) > 10:
                        self.long_term.store(fact)
        except Exception as e:
            logger.warning(f"Memory extraction failed: {e}")

    def get_context(self, query: str) -> str:
        memories = self.long_term.retrieve(query, top_k=5)
        if not memories:
            return ""
        return "\n".join(f"- {m}" for m in memories)

    def get_messages(self) -> List[BaseMessage]:
        return self.short_term.get_messages()

    def clear(self):
        self.short_term.clear()
