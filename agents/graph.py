from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import agent_node, tool_node, should_continue


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()
agent_graph = build_agent_graph()
