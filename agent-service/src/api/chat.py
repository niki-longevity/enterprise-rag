# 对话API路由
# 提供Java服务调用的对话接口
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import agent_graph
from src.db.session import get_db
from src.db.mapper import ChatHistoryMapper
from src.db.models import ChatHistory
import src.db

router = APIRouter()


class ChatRequest(BaseModel):
    """Java服务发来的对话请求"""
    userId: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    """回复附件，如引用的政策文档等"""
    type: str
    title: str


class ChatResponse(BaseModel):
    """返回给Java服务的对话响应"""
    reply: str
    session_id: str
    attachments: Optional[List[Attachment]] = None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    接收Java服务的对话请求，调用LangGraph Agent处理

    流程：
    1. 生成或获取会话ID
    2. 保存用户消息到数据库
    3. 调用LangGraph Agent生成回答
    4. 保存助手回复到数据库
    5. 返回响应
    """
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

    mapper = ChatHistoryMapper(db)

    user_msg = ChatHistory(
        session_id=session_id,
        user_id=request.userId,
        role="USER",
        content=request.message
    )
    mapper.save(user_msg)

    result = agent_graph.invoke(initial_state)
    reply = result["messages"][-1].content

    assistant_msg = ChatHistory(
        session_id=session_id,
        user_id=request.userId,
        role="ASSISTANT",
        content=reply
    )
    mapper.save(assistant_msg)

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        attachments=None
    )


@router.get("/history")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的历史消息"""
    mapper = ChatHistoryMapper(db)
    return mapper.list_by_session_id(session_id)


@router.get("/sessions")
def get_sessions(user_id: str, db: Session = Depends(get_db)):
    """获取用户的会话ID列表，按最后消息时间倒序"""
    mapper = ChatHistoryMapper(db)
    return mapper.list_session_ids_by_user_id(user_id)
