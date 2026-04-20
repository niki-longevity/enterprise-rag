# LangGraph节点实现
# 实现各个Agent节点功能
from typing import List
from src.agent.state import AgentState
from src.rag.retriever import get_policy_retriever
from src.tools.resource_tools import query_available_resources
from src.tools.ticket_tools import create_ticket


def classify_intent(state: AgentState) -> AgentState:
    """意图分类节点：识别用户意图"""
    message = state["message"].lower()

    # 简单关键词匹配实现意图分类
    policy_keywords = ["政策", "规定", "制度", "办法", "规范", "能不能", "可以吗", "允许吗", "怎么", "如何"]
    resource_keywords = ["资源", "设备", "投影仪", "笔记本", "会议室", "借用", "闲置"]
    ticket_keywords = ["申请", "审批", "工单", "帮我", "需要"]

    intent = "CHITCHAT"
    if any(kw in message for kw in policy_keywords):
        intent = "POLICY_QA"
    elif any(kw in message for kw in resource_keywords):
        intent = "RESOURCE_QUERY"
    elif any(kw in message for kw in ticket_keywords):
        intent = "TICKET_CREATE"

    state["intent"] = intent
    return state


def retrieve_policy_docs(state: AgentState) -> AgentState:
    """政策文档检索节点：从向量库检索相关政策"""
    query = state["message"]
    retriever = get_policy_retriever()
    docs = retriever.search(query, top_k=3)
    state["retrieved_docs"] = docs
    return state


def generate_policy_answer(state: AgentState) -> AgentState:
    """生成政策问答回答"""
    query = state["message"]
    docs = state.get("retrieved_docs", [])

    if not docs:
        state["answer"] = "抱歉，没有找到相关的政策信息。"
        return state

    # 简单的回答生成：拼接检索到的文档内容
    context = "\n\n".join([f"【{doc['title']}】\n{doc['content']}" for doc in docs])

    answer = f"根据您的问题「{query}」，我为您找到以下相关政策：\n\n{context}\n\n希望以上信息对您有帮助！"
    state["answer"] = answer
    return state


def query_resources_node(state: AgentState) -> AgentState:
    """资源查询节点：从Java服务查询资源"""
    message = state["message"].lower()

    # 简单的资源类型识别
    resource_type = None
    if "投影仪" in message:
        resource_type = "PROJECTOR"
    elif "笔记本" in message or "电脑" in message:
        resource_type = "LAPTOP"
    elif "会议室" in message:
        resource_type = "ROOM"
    elif "软件" in message or "许可" in message:
        resource_type = "LICENSE"

    # 查询可用资源
    if resource_type:
        from src.tools.resource_tools import query_resource
        resources = query_resource(resource_type=resource_type, status="AVAILABLE")
    else:
        resources = query_available_resources()

    state["resources"] = resources
    return state


def generate_resource_answer(state: AgentState) -> AgentState:
    """生成资源查询回答"""
    message = state["message"]
    resources = state.get("resources", [])

    if not resources:
        state["answer"] = "抱歉，目前没有找到可用的资源。"
        return state

    # 格式化资源列表
    resource_list = []
    for res in resources:
        type_name = {
            "PROJECTOR": "投影仪",
            "LAPTOP": "笔记本电脑",
            "ROOM": "会议室",
            "LICENSE": "软件许可"
        }.get(res.get("type"), res.get("type"))

        name = res.get('name', '')
        desc = res.get('description', '')
        quantity = res.get('quantity')
        available_quantity = res.get('availableQuantity') or res.get('available_quantity')

        if available_quantity is not None and quantity is not None:
            resource_list.append(f"- {type_name}: {name} (可用: {available_quantity}/{quantity}, {desc})")
        else:
            resource_list.append(f"- {type_name}: {name} ({desc})")

    answer = f"根据您的问题「{message}」，以下是可用的资源：\n\n" + "\n".join(resource_list)
    state["answer"] = answer
    return state


def generate_fallback_answer(state: AgentState) -> AgentState:
    """生成兜底回答"""
    intent = state["intent"]
    if intent == "TICKET_CREATE":
        state["answer"] = "工单申请功能正在开发中，敬请期待！"
    else:
        state["answer"] = "您好！我是企业员工助手，目前可以帮您查询政策信息和可用资源。请问有什么可以帮您的？"
    return state


def create_ticket_node(state: AgentState) -> AgentState:
    """工单创建节点：调用Java服务创建工单"""
    message = state["message"]
    user_id = state["user_id"]

    # 简单的工单类型识别
    ticket_type = "BORROW"
    if "请假" in message or "休假" in message:
        ticket_type = "LEAVE"
    elif "报销" in message or "差旅" in message:
        ticket_type = "EXPENSE"

    # 创建工单
    ticket = create_ticket(
        user_id=user_id,
        ticket_type=ticket_type,
        reason=message
    )
    state["ticket"] = ticket
    return state


def generate_ticket_answer(state: AgentState) -> AgentState:
    """生成工单创建回答"""
    ticket = state.get("ticket")
    if not ticket:
        state["answer"] = "抱歉，工单创建失败，请稍后再试。"
        return state

    ticket_no = ticket.get("ticketNo")
    status = ticket.get("status")
    status_text = {
        "PENDING": "待审批",
        "APPROVED": "已批准",
        "REJECTED": "已拒绝"
    }.get(status, status)

    answer = f"工单已创建成功！\n\n工单号：{ticket_no}\n当前状态：{status_text}"
    if status == "APPROVED":
        answer += "\n\n恭喜，您的申请已自动批准！"
    elif status == "REJECTED":
        answer += "\n\n抱歉，您的申请未通过审批。"
    else:
        answer += "\n\n请等待审批结果，我们会尽快处理您的申请。"

    state["answer"] = answer
    return state


def router_node(state: AgentState) -> str:
    """路由节点：根据意图选择下一个节点"""
    intent = state.get("intent")
    if intent == "POLICY_QA":
        return "retrieve_policy_docs"
    elif intent == "RESOURCE_QUERY":
        return "query_resources_node"
    elif intent == "TICKET_CREATE":
        return "create_ticket_node"
    else:
        return "generate_fallback_answer"
