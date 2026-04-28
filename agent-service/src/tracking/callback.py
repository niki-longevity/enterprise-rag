# LangChain BaseCallbackHandler — 自动拦截 ChatOpenAI 调用
# 兼容 streaming（astream_events）和非 streaming（invoke）两种模式
import time
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler

from src.auth.deps import _tracking_ctx
from src.tracking.recorder import record_llm_call


class LLMTrackingCallback(BaseCallbackHandler):
    """拦截 LLM 调用，记录 token/延迟/成本"""

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs):
        self._start_time = time.time()
        self._model_name = serialized.get("kwargs", {}).get("model_name", "unknown")
        self._recorded = False  # 防止 streaming 多次记录

    def on_llm_end(self, response, **kwargs):
        if self._recorded:
            return
        ctx = _tracking_ctx.get()
        if not ctx or not ctx.get("user_id"):
            return

        # 尝试从多个来源提取 token usage
        # 1. 非 streaming：llm_output.token_usage
        usage = {}
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})

        # 2. Streaming 最后 chunk：generations[0][0].message.usage_metadata
        if not usage and response.generations and response.generations[0]:
            gen = response.generations[0][0]
            if hasattr(gen, "message") and hasattr(gen.message, "usage_metadata"):
                m = gen.message.usage_metadata
                if m:
                    usage = {"prompt_tokens": m.get("input_tokens", 0),
                             "completion_tokens": m.get("output_tokens", 0)}

        # 3. generation_info
        if not usage and response.generations and response.generations[0]:
            gen = response.generations[0][0]
            if hasattr(gen, "generation_info") and gen.generation_info:
                gi = gen.generation_info
                if "input_tokens" in gi:
                    usage = {"prompt_tokens": gi.get("input_tokens", 0),
                             "completion_tokens": gi.get("output_tokens", 0)}

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # 只有有 token 数据时才记录（streaming 中间 chunk 没有 usage 数据）
        if input_tokens == 0 and output_tokens == 0:
            return

        self._recorded = True
        latency_ms = int((time.time() - self._start_time) * 1000)

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
        if self._recorded:
            return
        self._recorded = True
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
