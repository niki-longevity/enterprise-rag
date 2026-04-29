# 对话编排：记忆管理 + 流式对话核心逻辑
import json
import threading
from typing import Optional, AsyncGenerator

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.application.agent.graph import agent_graph
from src.application.agent.nodes import get_llm
from src.application.agent.guard import check_message
from src.shared.security import _tracking_ctx
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.mapper import ChatHistoryMapper
from src.domain.models import ChatHistory
from src.infrastructure.cache.redis import redis_client


def compress_memory_async(memory_key: str, user_id: str, session_id: str):
    """异步压缩记忆：在后台线程中运行"""
    import contextvars
    ctx_copy = contextvars.copy_context()

    def task():
        _tracking_ctx.set({"user_id": user_id, "session_id": session_id, "node_type": "compress"})
        memory_items = redis_client.lrange(memory_key, 0, -1)
        if len(memory_items) <= 20:
            return

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

    thread = threading.Thread(target=ctx_copy.run, args=(task,), daemon=True)
    thread.start()


async def chat_stream_impl(
    userId: str,
    message: str,
    sessionId: Optional[str],
    db: Session
):
    """流式对话核心逻辑：记忆加载 → guard → graph → 持久化"""
    session_id = sessionId or f"sess_{userId}_{id(userId)}"
    memory_key = f"{userId}:{session_id}"

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

    messages.append(SystemMessage(content="你是公司的政策、规定问询顾问。"
                                          "上面是与用户的历史会话，下面是用户的新问题，请确保回答内容量简练精要。"
                                          "只要是关于公司政策、规定的问询，严格根据检索到的内容来回答，严禁杜撰回答，不知道就告诉用户不知道、不了解之类的。"
                                        "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"))
    messages.append(HumanMessage(content=message))

    initial_state = {
        "messages": messages,
        "user_id": userId,
        "session_id": session_id,
    }

    user_msg = ChatHistory(session_id=session_id, user_id=userId, role="USER", content=message)
    mapper = ChatHistoryMapper(db)
    mapper.save(user_msg)

    async def generate() -> AsyncGenerator[str, None]:
        full_reply = ""
        try:
            is_safe, guard_reply = check_message(message)
            if not is_safe:
                full_reply = guard_reply
                yield f"data: {json.dumps({'type': 'content', 'content': guard_reply}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'end', 'session_id': session_id}, ensure_ascii=False)}\n\n"
                assistant_msg = ChatHistory(session_id=session_id, user_id=userId, role="ASSISTANT", content=guard_reply)
                mapper.save(assistant_msg)
                redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": message}, ensure_ascii=False))
                redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": guard_reply}, ensure_ascii=False))
                return

            _tracking_ctx.set({"user_id": userId, "session_id": session_id, "node_type": "agent"})
            async for event in agent_graph.astream_events(initial_state, version="v2", config={"recursion_limit": 8}):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        full_reply += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            assistant_msg = ChatHistory(session_id=session_id, user_id=userId, role="ASSISTANT", content=full_reply)
            mapper.save(assistant_msg)
            redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": message}, ensure_ascii=False))
            redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": full_reply}, ensure_ascii=False))

            if redis_client.llen(memory_key) > 20:
                compress_memory_async(memory_key, userId, session_id)

            yield f"data: {json.dumps({'type': 'end', 'session_id': session_id}, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"聊天接口异常：{str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
