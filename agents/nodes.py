from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from agents.state import AgentState
from tools import get_all_tools
from prompts.system import build_system_prompt
from backend.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=settings.openai_api_key)

_tools = get_all_tools()
_llm_with_tools = _llm.bind_tools(_tools)
_tool_map = {t.name: t for t in _tools}


def agent_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Core reasoning node: decide whether to call tools or respond directly."""
    context = "\n".join(filter(None, [
        state.get("retrieved_context", ""),
        state.get("rag_context", ""),
    ]))
    system_prompt = build_system_prompt(
        user_name=state.get("user_id", "User"),
        extra_context=context,
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    logger.debug(f"Agent node: {len(messages)} messages")
    response = _llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    """Execute whatever tool calls the agent requested."""
    last = state["messages"][-1]
    results = []
    for call in last.tool_calls:
        tool = _tool_map.get(call["name"])
        if tool is None:
            output = f"Tool '{call['name']}' not found."
        else:
            try:
                output = tool.invoke(call["args"])
            except Exception as exc:
                output = f"Error: {exc}"
        results.append(
            ToolMessage(content=str(output), tool_call_id=call["id"])
        )
    return {"messages": results}


def should_continue(state: AgentState) -> str:
    """Route: if the last message has tool calls, go to tools; else finish."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"
