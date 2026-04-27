# 对话API路由 - 流式输出
# 提供给前端服务调用的对话接口
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agent.graph import agent_graph
from src.agent.nodes import get_llm
from src.db.session import SessionLocal, get_db
from src.db.mapper import ChatHistoryMapper
from src.db.models import ChatHistory
from src.config.client import redis_client
import json
import threading


router = APIRouter()


def compress_memory_async(memory_key: str):
    """异步压缩记忆：在后台线程中运行"""
    def task():
        memory_items = redis_client.lrange(memory_key, 0, -1)
        if len(memory_items) <= 20:
            return

        # 保留最后3轮对话
        split_idx = max(0, len(memory_items) - 6)
        to_summarize = memory_items[:split_idx]
        to_keep = memory_items[split_idx:]

        history_text = "\n".join([
            f"{json.loads(item)['role']}: {json.loads(item)['content']}"
            for item in to_summarize
        ])
        summary_prompt = f"""请总结以下对话历史，简洁、准确地保留关键信息：
                        {history_text}
                        """
        llm = get_llm()
        summary = llm.invoke([HumanMessage(content=summary_prompt)]).content

        lua_script = """
                    redis.call('DEL', KEYS[1])
                    for i=1, #ARGV do
                        redis.call('RPUSH', KEYS[1], ARGV[i])
                    end
                    """
        new_items = [json.dumps({"role": "SUMMARY", "content": summary}, ensure_ascii=False)] + to_keep
        redis_client.eval(lua_script, 1, memory_key, *new_items)

    thread = threading.Thread(target=task, daemon=True)
    thread.start()


class ChatRequest(BaseModel):
    """前端发来的对话请求"""
    userId: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息内容")
    sessionId: Optional[str] = Field(None, description="会话ID，可选，用于会话续传")


class Attachment(BaseModel):
    """回复附件，如引用的政策文档等"""
    type: str
    title: str


async def chat_stream_impl(
    userId: str,
    message: str,
    sessionId: Optional[str],
    db: Session
):
    """流式对话核心逻辑"""
    session_id = sessionId or f"sess_{userId}_{id(userId)}"
    memory_key = f"{userId}:{session_id}"

    # 构建消息列表
    messages = []
    memory_items = redis_client.lrange(memory_key, 0, -1)
    for item in memory_items:
        msg = json.loads(item)
        if msg["role"] == "USER":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ASSISTANT":
            messages.append(AIMessage(content=msg["content"]))
        elif msg["role"] == "SUMMARY":
            messages.append(SystemMessage(content="历史对话摘要：" + msg["content"]))

    messages.append(SystemMessage(content="上面是与用户的历史会话，下面是用户的新问题，请确保回答内容量适中。"
                                  "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"))
    messages.append(HumanMessage(content=message))

    initial_state = {
        "messages": messages,
        "user_id": userId,
        "session_id": session_id,
    }

    # 先保存用户消息
    user_msg = ChatHistory(
        session_id=session_id,
        user_id=userId,
        role="USER",
        content=message
    )
    mapper = ChatHistoryMapper(db)
    mapper.save(user_msg)

    async def generate() -> AsyncGenerator[str, None]:
        full_reply = ""
        try:
            # 真正的流式：使用 astream_events 实时获取 LLM 输出
            async for event in agent_graph.astream_events(initial_state, version="v2", config={"recursion_limit": 20}):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        full_reply += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 流结束后保存数据
            assistant_msg = ChatHistory(
                session_id=session_id,
                user_id=userId,
                role="ASSISTANT",
                content=full_reply
            )
            mapper.save(assistant_msg)

            # 保存到 Redis
            redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": message}, ensure_ascii=False))
            redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": full_reply}, ensure_ascii=False))

            # 触发压缩
            if redis_client.llen(memory_key) > 20:
                compress_memory_async(memory_key)

            # 发送结束信号
            yield f"data: {json.dumps({'type': 'end', 'session_id': session_id}, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"聊天接口异常：{str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """流式对话接口"""
    return await chat_stream_impl(request.userId, request.message, request.sessionId, db)


@router.get("/history")
def get_history(session_id: str):
    """获取指定会话的历史消息"""
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)
    history = mapper.list_by_session_id(session_id)
    db.close()
    return history


@router.get("/sessions")
def get_sessions(user_id: str):
    """获取用户的会话ID列表，按最后消息时间倒序"""
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)
    sessions = mapper.list_session_ids_by_user_id(user_id)
    db.close()
    return sessions
