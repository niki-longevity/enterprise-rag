# 对话API路由
# 定义Java服务调用Agent的HTTP接口
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

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
    # TODO: 实现LangGraph调用逻辑
    session_id = request.session_id or f"sess_{request.user_id}_{id(request)}"
    return ChatResponse(
        reply=f"收到消息：{request.message}",
        session_id=session_id,
        attachments=None
    )
