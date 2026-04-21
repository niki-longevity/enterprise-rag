# Agent工具定义
from langchain_core.tools import tool
from src.tools.resource_tools import query_resource, query_available_resources
from src.tools.ticket_tools import create_ticket as _create_ticket
from src.rag.retriever import search


@tool
def search_policy(query: str) -> str:
    """搜索公司政策文档，回答用户关于政策、规定、制度的问题
    Args:
        query: 用户的问题，如"请假需要提前几天申请？"
    """
    print("提问：", query)
    docs = search(query, top_k=3)
    return docs


@tool
def search_resources(resource_type: str = None) -> str:
    """查询公司可用资源，如投影仪、笔记本电脑、会议室、软件许可等
    Args:
        resource_type: 可选，资源类型，有效值：PROJECTOR（投影仪）、LAPTOP（笔记本电脑）、ROOM（会议室）、LICENSE（软件许可）
    """
    if resource_type:
        resources = query_resource(resource_type=resource_type, status="AVAILABLE")
    else:
        resources = query_available_resources()
    if not resources:
        return "当前没有可用资源。"
    return "\n\n".join([
        f"[{r.get('name')}]\n类型: {r.get('type')}\n状态: {r.get('status')}"
        for r in resources
    ])


@tool
def create_ticket(user_id: str, ticket_type: str, reason: str) -> str:
    """创建工单申请，如请假、报销、借用资源等
    Args:
        user_id: 用户ID
        ticket_type: 工单类型，有效值：BORROW（借用）、LEAVE（请假）、EXPENSE（报销）
        reason: 申请原因或说明
    """
    ticket = _create_ticket(user_id=user_id, ticket_type=ticket_type, reason=reason)
    if ticket:
        return f"工单创建成功！工单号: {ticket.get('ticketNo')}, 状态: {ticket.get('status')}"
    return "工单创建失败，请稍后重试。"


tools = [search_policy, search_resources, create_ticket]
