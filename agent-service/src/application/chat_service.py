# 对话编排服务
# 整个对话流程的"指挥中心"：记忆管理、防注入检查、图调用、回复持久化
# presentation/chat.py 的路由只做参数绑定，真正的业务逻辑都在这里

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
    """超过 20 条消息时，将历史对话压缩为一条摘要，异步执行不阻塞响应。

    压缩策略：保留最后 3 轮（6 条），前面的全部用 LLM 总结成一条 SUMMARY。
    Redis Lua 脚本原子替换整个列表，避免并发问题。

    Args:
        memory_key: Redis key，格式 "{user_id}:{session_id}"
        user_id: 当前用户 ID
        session_id: 当前会话 ID
    """
    import contextvars
    ctx_copy = contextvars.copy_context()

    def task():
        # 设置追踪上下文，让 cost tracking callback 能记录这次 LLM 调用
        _tracking_ctx.set({"user_id": user_id, "session_id": session_id, "node_type": "compress"})

        memory_items = redis_client.lrange(memory_key, 0, -1)
        if len(memory_items) <= 20:
            return

        # 保留最后 3 轮对话（6 条消息），前面的全部压缩
        split_idx = max(0, len(memory_items) - 6)
        to_summarize = memory_items[:split_idx]
        to_keep = memory_items[split_idx:]

        # 组装历史文本，调用 LLM 生成摘要
        history_text = "\n".join([
            f"{json.loads(item)['role']}: {json.loads(item)['content']}"
            for item in to_summarize
        ])
        summary_prompt = f"""请总结以下对话历史，简洁、准确地保留关键信息：
                        {history_text}
                        """
        llm = get_llm()
        summary = llm.invoke([HumanMessage(content=summary_prompt)]).content

        # Lua 脚本：原子地删除旧列表 + 写入摘要 + 保留最后 3 轮
        lua_script = """
                    redis.call('DEL', KEYS[1])
                    for i=1, #ARGV do
                        redis.call('RPUSH', KEYS[1], ARGV[i])
                    end
                    """
        new_items = [json.dumps({"role": "SUMMARY", "content": summary}, ensure_ascii=False)] + to_keep
        redis_client.eval(lua_script, 1, memory_key, *new_items)

    # contextvars.copy_context().run() 确保后台线程能读取到调用方的上下文
    thread = threading.Thread(target=ctx_copy.run, args=(task,), daemon=True)
    thread.start()


async def chat_stream_impl(
    userId: str,
    message: str,
    sessionId: Optional[str],
    db: Session
):
    """流式对话的完整编排，返回 SSE StreamingResponse。

    流程：
    1. 从 Redis 加载历史记忆，构建 LangChain 消息列表
    2. 拼接 System Prompt（公司政策问答顾问角色定义）
    3. 保存用户消息到 MySQL
    4. 调用防注入守卫 → 命中则直接返回拒答
    5. 走 LangGraph ReAct 图（agent ⇄ tools），流式 yield LLM token
    6. 保存助手回复到 MySQL + Redis
    7. 超过 20 条触发异步记忆压缩

    Args:
        userId: JWT 解析出的用户 ID
        message: 用户输入
        sessionId: 会话 ID，None 则自动生成
        db: 数据库会话（由 FastAPI Depends 注入）
    """
    # ── 1. 初始化会话 ─────────────────────────────────
    session_id = sessionId or f"sess_{userId}_{id(userId)}"
    memory_key = f"{userId}:{session_id}"

    # ── 2. 加载历史记忆 ───────────────────────────────
    messages = []
    memory_items = redis_client.lrange(memory_key, 0, -1)
    for item in memory_items:
        msg = json.loads(item)
        if msg["role"] == "USER":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ASSISTANT":
            messages.append(AIMessage(content=msg["content"]))
        elif msg["role"] == "SUMMARY":
            # 压缩后的摘要以 SystemMessage 形式注入，帮助 LLM 理解上下文
            messages.append(SystemMessage(content="历史对话摘要：" + msg["content"]))

    # ── 3. 系统提示词 ─────────────────────────────────
    messages.append(SystemMessage(content="你是公司的政策、规定问询顾问。"
                                          "上面是与用户的历史会话，下面是用户的新问题，请确保回答内容量简练精要。"
                                          "只要是关于公司政策、规定的问询，严格根据检索到的内容来回答，严禁杜撰回答，不知道就告诉用户不知道、不了解之类的。"
                                        "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"))
    messages.append(HumanMessage(content=message))

    # ── 4. 构建图初始状态 + 保存用户消息 ──────────────
    initial_state = {
        "messages": messages,
        "user_id": userId,
        "session_id": session_id,
    }

    user_msg = ChatHistory(session_id=session_id, user_id=userId, role="USER", content=message)
    mapper = ChatHistoryMapper(db)
    mapper.save(user_msg)

    async def generate() -> AsyncGenerator[str, None]:
        """SSE 流生成器：逐 token yield 给前端"""
        full_reply = ""
        try:
            # ── 5. 防注入守卫（在图外运行，不污染 astream_events） ──
            is_safe, guard_reply = check_message(message)
            if not is_safe:
                full_reply = guard_reply
                yield f"data: {json.dumps({'type': 'content', 'content': guard_reply}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'end', 'session_id': session_id}, ensure_ascii=False)}\n\n"
                # 保存 guard 回复
                assistant_msg = ChatHistory(session_id=session_id, user_id=userId, role="ASSISTANT", content=guard_reply)
                mapper.save(assistant_msg)
                redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": message}, ensure_ascii=False))
                redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": guard_reply}, ensure_ascii=False))
                return

            # ── 6. ReAct 图执行（流式） ──
            # 设置追踪上下文，cost tracking callback 据此记录 token/成本
            _tracking_ctx.set({"user_id": userId, "session_id": session_id, "node_type": "agent"})
            async for event in agent_graph.astream_events(initial_state, version="v2", config={"recursion_limit": 8}):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        full_reply += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # ── 7. 持久化 ──────────────────────────────
            assistant_msg = ChatHistory(session_id=session_id, user_id=userId, role="ASSISTANT", content=full_reply)
            mapper.save(assistant_msg)
            # Redis 记忆：用户消息 + 助手回复
            redis_client.rpush(memory_key, json.dumps({"role": "USER", "content": message}, ensure_ascii=False))
            redis_client.rpush(memory_key, json.dumps({"role": "ASSISTANT", "content": full_reply}, ensure_ascii=False))

            # ── 8. 触发记忆压缩 ─────────────────────────
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
