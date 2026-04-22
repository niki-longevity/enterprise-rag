# 对话API路由
# 提供给前端服务调用的对话接口
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import agent_graph
from src.db.session import SessionLocal
from src.db.mapper import ChatHistoryMapper
from src.db.models import ChatHistory
from src.db.session import get_db
from src.db.redis import redis_client
import json

router = APIRouter()


class ChatRequest(BaseModel):
    """前端发来的对话请求"""
    userId: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    """回复附件，如引用的政策文档等"""
    type: str
    title: str


class ChatResponse(BaseModel):
    """返回给前端的对话响应"""
    reply: str
    session_id: str
    attachments: Optional[List[Attachment]] = None


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    # 🔥 关键：注入数据库会话（自动创建、自动关闭，无需手动管理）
    db: Session = Depends(get_db)
):
    """
    接收前端的对话请求，调用LangGraph Agent处理
    修复：使用FastAPI依赖管理数据库会话，解决连接超时/存储失败问题
    """
    # 生成会话ID，如果没有传的话
    session_id = request.sessionId or f"sess_{request.userId}_{id(request)}"

    # 构建系统提示词
    system_prompt = "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"

    # 构建LangGraph初始状态
    initial_state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.message)
        ],
        "user_id": request.userId,
        "session_id": session_id,
    }

    # 🔥 直接使用注入的db会话，无需手动创建
    mapper = ChatHistoryMapper(db)

    try:
        # 保存用户消息
        user_msg = ChatHistory(
            session_id=session_id,
            user_id=request.userId,
            role="USER",
            content=request.message
        )
        mapper.save(user_msg)

        # 调用Agent生成回答（耗时操作，pool_pre_ping会自动保活连接）
        result = agent_graph.invoke(initial_state)
        reply = result["messages"][-1].content

        # 保存助手回复
        assistant_msg = ChatHistory(
            session_id=session_id,
            user_id=request.userId,
            role="ASSISTANT",
            content=reply
        )
        mapper.save(assistant_msg)

        # 保存到Redis长期记忆（list结构，key=userId:sessionId）
        memory_key = f"{request.userId}:{session_id}"
        redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": request.message}, ensure_ascii=False))
        redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": reply}, ensure_ascii=False))

    except Exception as e:
        # 捕获所有异常，返回错误，数据库会自动回滚
        print(f"聊天接口异常：{str(e)}")
        raise HTTPException(status_code=500, detail=f"处理消息失败：{str(e)}")

    # reply = reply.replace('\\n', '\n')
    # 返回响应
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        attachments=None
    )


@router.get("/history")
def get_history(session_id: str):
    """获取指定会话的历史消息"""
    # 创建数据库会话，和test_db一样
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)

    # 查询会话历史，用mapper，和test_db一样
    history = mapper.list_by_session_id(session_id)

    # 关闭数据库会话
    db.close()

    return history


@router.get("/sessions")
def get_sessions(user_id: str):
    """获取用户的会话ID列表，按最后消息时间倒序"""
    # 创建数据库会话，和test_db一样
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)

    # 查询会话列表，用mapper，和test_db一样
    sessions = mapper.list_session_ids_by_user_id(user_id)

    # 关闭数据库会话
    db.close()

    return sessions
