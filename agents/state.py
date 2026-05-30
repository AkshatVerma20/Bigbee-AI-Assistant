from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    session_id: str
    retrieved_context: str   # Long-term memory context
    rag_context: str         # RAG document context
    final_response: str
