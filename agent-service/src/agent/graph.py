# LangGraph图定义 - ReAct模式（含前置防注入守卫）
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, tool_node, should_continue
from src.agent.guard import guard_node, should_guard


def create_agent_graph():
    """创建带防注入守卫的 ReAct LangGraph 状态图"""
    graph = StateGraph(AgentState)

    graph.add_node("guard", guard_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("guard")

    graph.add_conditional_edges(
        "guard",
        should_guard,
        {"agent": "agent", "end": END}
    )

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


agent_graph = create_agent_graph()
