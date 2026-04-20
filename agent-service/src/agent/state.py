# LangGraph状态定义
# 定义Agent在执行过程中维护的状态数据结构
from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    # 基础信息
    user_id: str  # 用户ID
    session_id: str  # 会话ID
    message: str  # 用户原始消息

    # 需求理解结果
    intent: Optional[str]  # 用户意图：POLICY_QA, RESOURCE_QUERY, TICKET_CREATE, CHITCHAT

    # RAG检索相关
    retrieved_docs: List[dict]  # 检索到的政策文档

    # 资源查询相关
    resources: List[dict]  # 查询到的资源列表

    # 工单创建相关
    ticket: Optional[dict]  # 创建的工单信息

    # 最终输出
    answer: Optional[str]  # 最终回答内容
