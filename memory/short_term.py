from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ShortTermMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._messages: List[BaseMessage] = []

    def add_user_message(self, content: str):
        self._messages.append(HumanMessage(content=content))
        self._trim()

    def add_ai_message(self, content: str):
        self._messages.append(AIMessage(content=content))
        self._trim()

    def get_messages(self) -> List[BaseMessage]:
        return list(self._messages)

    def clear(self):
        self._messages = []

    def _trim(self):
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def to_dict_list(self) -> List[dict]:
        result = []
        for m in self._messages:
            if isinstance(m, HumanMessage):
                result.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                result.append({"role": "assistant", "content": m.content})
        return result
