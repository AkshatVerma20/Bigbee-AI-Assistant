from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

from agents.graph import agent_graph
from agents.state import AgentState
from memory.manager import MemoryManager
from langchain_core.messages import HumanMessage
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# In-memory session store (replace with Redis for multi-process production)
_sessions: dict = {}


def get_memory(user_id: str, session_id: str) -> MemoryManager:
    key = f"{user_id}:{session_id}"
    if key not in _sessions:
        _sessions[key] = MemoryManager(user_id=user_id, session_id=session_id)
    return _sessions[key]


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    session_id: str = "default"
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: list = []


class MultiAgentRequest(BaseModel):
    task: str
    user_id: str = "default"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    try:
        memory = get_memory(request.user_id, request.session_id)
        context = memory.get_context(request.message)
        initial_state: AgentState = {
            "messages": memory.get_messages() + [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "session_id": request.session_id,
            "retrieved_context": context,
            "rag_context": "",
            "final_response": "",
        }

        if request.stream:
            return StreamingResponse(
                _stream_response(initial_state, memory, request),
                media_type="text/event-stream",
            )

        result = await asyncio.to_thread(agent_graph.invoke, initial_state)
        final_message = result["messages"][-1].content
        memory.add_exchange(request.message, final_message)
        return ChatResponse(response=final_message, session_id=request.session_id)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(500, str(e))


async def _stream_response(initial_state, memory, request: ChatRequest):
    full_response = []
    try:
        for chunk in agent_graph.stream(initial_state, stream_mode="values"):
            last_msg = chunk["messages"][-1]
            # Only emit final text content (not tool calls)
            if hasattr(last_msg, "content") and last_msg.content and not getattr(last_msg, "tool_calls", None):
                content = last_msg.content
                if content not in full_response:
                    full_response = [content]
                    yield f"data: {json.dumps({'token': content, 'done': False})}\n\n"
        final = full_response[-1] if full_response else ""
        if final:
            memory.add_exchange(request.message, final)
        yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"


@router.post("/multi-agent")
async def multi_agent_chat(request: MultiAgentRequest):
    from agents.multi_agent import multi_agent_graph, MultiAgentState
    try:
        initial_state: MultiAgentState = {
            "messages": [],
            "task": request.task,
            "research_result": "",
            "code_result": "",
            "next_agent": "",
            "final_answer": "",
            "iteration": 0,
        }
        result = await asyncio.to_thread(multi_agent_graph.invoke, initial_state)
        return {
            "answer": result.get("final_answer", "No answer generated"),
            "research": result.get("research_result", ""),
            "code": result.get("code_result", ""),
        }
    except Exception as e:
        logger.error(f"Multi-agent error: {e}", exc_info=True)
        raise HTTPException(500, str(e))
