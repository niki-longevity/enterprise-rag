# 对话 API 路由
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from src.shared.security import get_current_user
from src.application.quota import check_quota
from src.application.chat_service import chat_stream_impl
from src.infrastructure.database.session import SessionLocal, get_db
from src.infrastructure.database.mapper import ChatHistoryMapper

router = APIRouter()


class ChatRequest(BaseModel):
    """前端发来的对话请求"""
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    quota_info: dict = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """流式对话接口"""
    return await chat_stream_impl(user_id, request.message, request.sessionId, db)


@router.get("/history")
def get_history(session_id: str, user_id: str = Depends(get_current_user)):
    """获取指定会话的历史消息"""
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)
    history = mapper.list_by_session_id(session_id)
    db.close()
    return history


@router.get("/sessions")
def get_sessions(user_id: str = Depends(get_current_user)):
    """获取用户的会话ID列表，按最后消息时间倒序"""
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)
    sessions = mapper.list_session_ids_by_user_id(user_id)
    db.close()
    return sessions
