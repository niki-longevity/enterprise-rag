# LangGraph节点实现 - ReAct模式
from typing import Literal
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from src.rag.retriever import get_policy_retriever
from src.tools.resource_tools import query_available_resources, query_resource
from src.tools.ticket_tools import create_ticket
from src.llm.llm import get_llm_with_tools


@tool
def search_policy(query: str) -> str:
    """搜索政策文档，回答用户关于公司政策、规定、制度的问题"""
    retriever = get_policy_retriever()
    docs = retriever.search(query, top_k=3)
    if not docs:
        return "没有找到相关政策信息。"
    return "\n\n".join([f"[{doc['title']}]\n{doc['content']}" for doc in docs])


@tool
def query_resources(resource_type: str = None) -> str:
    """查询公司可用资源，如投影仪、笔记本电脑、会议室、软件许可等

    Args:
        resource_type: 可选，资源类型，如 PROJECTOR（投影仪）、LAPTOP（笔记本）、ROOM（会议室）、LICENSE（软件许可）
    """
    if resource_type:
        resources = query_resource(resource_type=resource_type, status="AVAILABLE")
    else:
        resources = query_available_resources()
    if not resources:
        return "目前没有可用资源。"
    return "\n\n".join([f"[{r['name']}]\n类型: {r['type']}\n状态: {r['status']}" for r in resources])


@tool
def create_ticket_tool(user_id: str, ticket_type: str, reason: str) -> str:
    """创建工单申请，如请假、报销、借用资源等

    Args:
        user_id: 用户ID
        ticket_type: 工单类型，如 BORROW（借用）、LEAVE（请假）、EXPENSE（报销）
        reason: 申请原因
    """
    ticket = create_ticket(user_id=user_id, ticket_type=ticket_type, reason=reason)
    if ticket:
        return f"工单创建成功！工单号：{ticket['id']}，类型：{ticket['type']}"
    return "工单创建失败，请稍后再试。"


tools = [search_policy, query_resources, create_ticket_tool]


def agent_node(state):
    """LLM节点：决定调用工具还是直接回答"""
    llm = get_llm_with_tools(tools)
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state) -> Literal["tools", "end"]:
    """路由：判断是否需要调用工具"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


def tool_node(state):
    """工具节点：执行工具调用"""
    messages = state["messages"]
    last_message = messages[-1]

    tool_outputs = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "search_policy":
            output = search_policy.invoke(tool_args)
        elif tool_name == "query_resources":
            output = query_resources.invoke(tool_args)
        elif tool_name == "create_ticket_tool":
            output = create_ticket_tool.invoke(tool_args)
        else:
            output = f"未知工具: {tool_name}"

        tool_outputs.append(
            ToolMessage(content=output, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_outputs}
