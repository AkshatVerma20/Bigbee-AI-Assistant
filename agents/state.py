from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    session_id: str
    retrieved_context: str  
    rag_context: str        
    final_response: str
