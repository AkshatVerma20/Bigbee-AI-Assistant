"""
Multi-agent system: Supervisor + Researcher + Coder + Writer.
Use via POST /api/multi-agent for complex multi-step tasks.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator

from backend.config import settings
from tools.code_executor import python_repl
from utils.logger import get_logger

logger = get_logger(__name__)


class MultiAgentState(TypedDict):
    messages: Annotated[List, operator.add]
    task: str
    research_result: str
    code_result: str
    next_agent: str
    final_answer: str
    iteration: int


_supervisor_llm = ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key, temperature=0)
_specialist_llm = ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key, temperature=0.7)


def supervisor_node(state: MultiAgentState) -> dict:
    iteration = state.get("iteration", 0) + 1
    # Prevent infinite loops
    if iteration > 4:
        return {"next_agent": "FINISH", "iteration": iteration}

    prompt = (
        f"You are a task supervisor. Decide the next step for this task.\n"
        f"Task: {state['task']}\n"
        f"Research done: {'Yes' if state.get('research_result') else 'No'}\n"
        f"Code done: {'Yes' if state.get('code_result') else 'No'}\n\n"
        f"Options: researcher | coder | writer | FINISH\n"
        f"Rules:\n"
        f"- If task needs current info and research not done → researcher\n"
        f"- If task needs code/analysis and code not done → coder\n"
        f"- If enough info gathered → writer\n"
        f"- If complete → FINISH\n\n"
        f"Respond with ONE word only."
    )
    resp = _supervisor_llm.invoke([HumanMessage(content=prompt)])
    decision = resp.content.strip().lower()
    if decision not in ("researcher", "coder", "writer"):
        decision = "writer" if state.get("research_result") else "researcher"
    logger.info(f"Supervisor → {decision} (iteration {iteration})")
    return {"next_agent": decision, "iteration": iteration}


def researcher_node(state: MultiAgentState) -> dict:
    from tools.web_search import get_web_search_tool
    try:
        search = get_web_search_tool()
        results = search.invoke({"query": state["task"]})
        summary_prompt = f"Summarize these search results for: '{state['task']}'\n\n{results}"
        summary = _specialist_llm.invoke([HumanMessage(content=summary_prompt)])
        return {"research_result": summary.content}
    except Exception as e:
        return {"research_result": f"Research skipped (no Tavily key?): {e}"}


def coder_node(state: MultiAgentState) -> dict:
    prompt = (
        f"Write Python code to help with: {state['task']}\n"
        f"Context: {state.get('research_result', 'None')}\n"
        f"Return ONLY executable Python code, no markdown fences."
    )
    code_resp = _specialist_llm.invoke([HumanMessage(content=prompt)])
    code = code_resp.content.strip()
    if "```" in code:
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[6:]
    execution = python_repl.invoke({"code": code})
    return {"code_result": f"Code:\n{code}\n\nOutput:\n{execution}"}


def writer_node(state: MultiAgentState) -> dict:
    prompt = (
        f"Write a comprehensive response for: {state['task']}\n\n"
        f"Research findings:\n{state.get('research_result', 'N/A')}\n\n"
        f"Code & analysis:\n{state.get('code_result', 'N/A')}\n\n"
        f"Provide a well-structured, clear answer."
    )
    resp = _specialist_llm.invoke([HumanMessage(content=prompt)])
    return {
        "final_answer": resp.content,
        "messages": [AIMessage(content=resp.content)],
    }


def route_supervisor(state: MultiAgentState) -> str:
    return state.get("next_agent", "writer")


def build_multi_agent_graph():
    graph = StateGraph(MultiAgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("coder", coder_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", route_supervisor, {
        "researcher": "researcher",
        "coder": "coder",
        "writer": "writer",
        "FINISH": END,
    })
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("coder", "supervisor")
    graph.add_edge("writer", END)
    return graph.compile()


multi_agent_graph = build_multi_agent_graph()
