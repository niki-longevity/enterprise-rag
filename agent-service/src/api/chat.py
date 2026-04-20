# 对话API路由
# 定义Java服务调用Agent的HTTP接口
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from src.agent.graph import agent_graph
from src.agent.state import AgentState

router = APIRouter()


class ChatRequest(BaseModel):
    # Java服务发来的对话请求
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    # 回复附件，如引用的政策文档、工单信息等
    type: str  # 类型：POLICY, RESOURCE, TICKET
    title: str  # 标题


class ChatResponse(BaseModel):
    # 返回给Java服务的对话响应
    reply: str  # 助手回复内容
    session_id: str  # 会话ID
    attachments: Optional[List[Attachment]] = None  # 附件列表


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # 接收Java服务的对话请求，调用LangGraph Agent处理
    session_id = request.session_id or f"sess_{request.user_id}_{id(request)}"

    # 构建初始状态
    initial_state: AgentState = {
        "user_id": request.user_id,
        "session_id": session_id,
        "message": request.message,
        "intent": None,
        "retrieved_docs": [],
        "resources": [],
        "ticket": None,
        "answer": None,
    }

    # 调用LangGraph
    result = agent_graph.invoke(initial_state)

    return ChatResponse(
        reply=result.get("answer", ""),
        session_id=session_id,
        attachments=None
    )
