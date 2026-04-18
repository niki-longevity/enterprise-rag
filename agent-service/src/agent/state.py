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
    # tasks: List[Task]  # 后续添加：拆解后的任务列表

    # 工具调用相关
    # current_task_index: int  # 后续添加：当前处理的任务索引
    # tool_calls: List  # 后续添加：工具调用记录
    # tool_results: List  # 后续添加：工具调用结果

    # RAG检索相关
    # retrieved_docs: List  # 后续添加：检索到的政策文档

    # 最终输出
    answer: Optional[str]  # 最终回答内容
    # attachments: List  # 后续添加：附件信息（政策文档、工单等）
