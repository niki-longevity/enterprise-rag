# LangGraph图定义
# 定义Agent的执行流程图（先做简化版，只有入口和结束节点，后续逐步添加节点）
from langgraph.graph import StateGraph, END
from src.agent.state import AgentState


def create_agent_graph():
    # 创建LangGraph状态图
    graph = StateGraph(AgentState)

    # TODO: 后续添加节点：
    # 1. 需求理解节点（意图识别+任务拆解）
    # 2. 政策问答分支（RAG检索）
    # 3. 资源查询分支
    # 4. 审批流分支（创建工单）
    # 5. 回答生成节点

    # 暂时直接连接开始到结束
    graph.set_entry_point("placeholder")
    graph.add_node("placeholder", placeholder_node)
    graph.add_edge("placeholder", END)

    # 编译图
    return graph.compile()


def placeholder_node(state: AgentState) -> AgentState:
    # 占位节点：直接返回简单回答
    # 后续会替换为真正的意图识别、任务拆解等节点
    state["answer"] = f"收到消息：{state['message']}（placeholder节点）"
    return state


# 全局Agent图实例
agent_graph = create_agent_graph()
