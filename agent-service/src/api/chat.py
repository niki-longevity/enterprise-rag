# 对话API路由
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import HumanMessage
from src.agent.graph import agent_graph

router = APIRouter()


class ChatRequest(BaseModel):
    userId: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    type: str
    title: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    attachments: Optional[List[Attachment]] = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.sessionId or f"sess_{request.userId}_{id(request)}"

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
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
