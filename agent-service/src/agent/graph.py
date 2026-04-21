# LangGraph图定义 - ReAct模式
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, tool_node, should_continue


def create_agent_graph():
    """创建ReAct模式的LangGraph状态图"""
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


agent_graph = create_agent_graph()

# try:
#     graph_image_bytes = agent_graph.get_graph().draw_mermaid_png()
#     with open("graph.png", "wb") as f:
#         f.write(graph_image_bytes)
# except Exception as e:
#     print("⚠️ 生成流程图失败:", e)
