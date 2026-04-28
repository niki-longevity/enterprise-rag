# LangChain BaseCallbackHandler — 自动拦截 ChatOpenAI 调用
import time
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler

from src.auth.deps import _tracking_ctx
from src.tracking.recorder import record_llm_call


class LLMTrackingCallback(BaseCallbackHandler):
    """拦截 LLM 调用，记录 token/延迟/成本"""

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs):
        # 存储开始时间
        self._start_time = time.time()
        # 提取 model name
        self._model_name = serialized.get("kwargs", {}).get("model", "unknown")

    def on_llm_end(self, response, **kwargs):
        ctx = _tracking_ctx.get()
        if not ctx or not ctx.get("user_id"):
            return  # 无上下文（如测试脚本），跳过

        latency_ms = int((time.time() - self._start_time) * 1000)

        # 从 response.llm_output 提取 token 用量
        usage = {}
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        record_llm_call(
            user_id=ctx["user_id"],
            session_id=ctx.get("session_id") or "",
            model_name=self._model_name,
            model_type="chat",
            node_type=ctx.get("node_type") or "agent",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )

    def on_llm_error(self, error, **kwargs):
        ctx = _tracking_ctx.get()
        if not ctx or not ctx.get("user_id"):
            return

        record_llm_call(
            user_id=ctx["user_id"],
            session_id=ctx.get("session_id") or "",
            model_name=self._model_name,
            model_type="chat",
            node_type=ctx.get("node_type") or "agent",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            status="error",
            error_msg=str(error)[:256],
        )


tracking_callback = LLMTrackingCallback()
