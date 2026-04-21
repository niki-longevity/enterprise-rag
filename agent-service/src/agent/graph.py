# LangGraph图定义
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import (
    classify_intent,
    retrieve_policy_docs,
    generate_policy_answer,
    query_resources_node,
    generate_resource_answer,
    create_ticket_node,
    generate_ticket_answer,
    generate_fallback_answer,
    router_node
)


def create_agent_graph():
    """创建LangGraph状态图"""
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("意图识别", classify_intent)
    graph.add_node("retrieve_policy_docs", retrieve_policy_docs)
    graph.add_node("generate_policy_answer", generate_policy_answer)
    graph.add_node("query_resources_node", query_resources_node)
    graph.add_node("generate_resource_answer", generate_resource_answer)
    graph.add_node("create_ticket_node", create_ticket_node)
    graph.add_node("generate_ticket_answer", generate_ticket_answer)
    graph.add_node("generate_fallback_answer", generate_fallback_answer)

    # 定义边
    graph.set_entry_point("意图识别")

    # 条件边：根据意图路由
    graph.add_conditional_edges(
        source="意图识别",
        path=router_node,
        path_map={
            "retrieve_policy_docs": "retrieve_policy_docs",
            "query_resources_node": "query_resources_node",
            "create_ticket_node": "create_ticket_node",
            "generate_fallback_answer": "generate_fallback_answer"
        }
    )

    graph.add_edge("retrieve_policy_docs", "generate_policy_answer")
    graph.add_edge("generate_policy_answer", END)
    graph.add_edge("query_resources_node", "generate_resource_answer")
    graph.add_edge("generate_resource_answer", END)
    graph.add_edge("create_ticket_node", "generate_ticket_answer")
    graph.add_edge("generate_ticket_answer", END)
    graph.add_edge("generate_fallback_answer", END)

    # 编译图
    return graph.compile()


# 全局Agent图实例
agent_graph = create_agent_graph()

# 流程可视化
try:
    graph_image_bytes = agent_graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(graph_image_bytes)
except Exception as e:
    print("⚠️ 生成流程图失败，可能是缺失依赖（需确联接互联网）:", e)