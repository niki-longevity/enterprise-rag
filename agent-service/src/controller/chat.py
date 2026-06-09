"""对话 API 路由

三层架构：controller 只负责参数绑定和调用 service，不碰 dao / model / infrastructure。

依赖注入链（由 FastAPI Depends 自动执行）：
  get_current_user → 解析 JWT，返回 user_id（未登录直接 401）
  check_quota     → 检查 RPM / 日请求数 / 日 Token 是否超额（超额 429）
  get_db          → 提供 SQLAlchemy 数据库会话
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from src.shared.security import get_current_user    # JWT 鉴权依赖
from src.service.quota import check_quota            # 三层限流依赖
from src.service.chat import chat_stream_impl, get_session_history, get_user_sessions
from src.dao.session import get_db                   # 仅用做 FastAPI Depends，不直接操作 DB

router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求体，前端传入 message 和可选 sessionId"""
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话 ID，不传则自动生成新会话")


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),        # JWT → user_id，未登录自动 401
    quota_info: dict = Depends(check_quota),          # 配额检查，超额自动 429
    db: Session = Depends(get_db)                     # DB 会话，由 service 层使用
):
    """流式对话接口，返回 SSE（Server-Sent Events）"""
    return await chat_stream_impl(user_id, request.message, request.sessionId, db)


@router.get("/history")
def get_history(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """查询指定会话的历史消息列表"""
    return get_session_history(session_id, user_id)


@router.get("/sessions")
def get_sessions(user_id: str = Depends(get_current_user)):
    """查询当前用户的所有会话 ID，按最后消息时间倒序排列"""
    return get_user_sessions(user_id)
