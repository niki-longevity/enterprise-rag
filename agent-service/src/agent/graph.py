# LangGraph图定义 - ReAct模式
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, tool_node, should_continue


def create_agent_graph():
    """创建 ReAct 模式的 LangGraph 状态图（防注入守卫在 chat.py 层提前拦截）"""
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


agent_graph = create_agent_graph()
