from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import agent_graph

router = APIRouter()    # 创建API路由

class ChatRequest(BaseModel):
    """Java服务发来的对话请求"""
    userId: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    """回复附件，如引用的政策文档、工单信息等"""
    type: str
    title: str


class ChatResponse(BaseModel):
    """返回给Java服务的对话响应"""
    reply: str
    session_id: str
    attachments: Optional[List[Attachment]] = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """接收Java服务的对话请求，调用LangGraph Agent处理"""
    session_id = request.sessionId or f"sess_{request.userId}_{id(request)}"

    system_prompt = "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"

    initial_state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.message)
        ],
        "user_id": request.userId,
        "session_id": session_id,
    }

    result = agent_graph.invoke(initial_state)
    reply = result["messages"][-1].content

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        attachments=None
    )
