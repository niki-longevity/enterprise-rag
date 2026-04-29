# DB 写入 + 手动埋点函数
import json
import time
from pathlib import Path
from src.db.session import SessionLocal
from src.domain.models import LLMCallLog


_pricing = None


def _load_pricing():
    global _pricing
    if _pricing is None:
        path = Path(__file__).parent / "pricing.json"
        _pricing = json.loads(path.read_text(encoding="utf-8"))


def _calc_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    _load_pricing()
    price = _pricing.get(model_name)
    if not price:
        return 0.0
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1000


def record_llm_call(
    user_id: str,
    session_id: str,
    model_name: str,
    model_type: str,
    node_type: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    status: str = "success",
    error_msg: str | None = None,
):
    db = SessionLocal()
    try:
        log = LLMCallLog(
            user_id=user_id,
            session_id=session_id,
            model_name=model_name,
            model_type=model_type,
            node_type=node_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost=_calc_cost(model_name, input_tokens, output_tokens),
            status=status,
            error_msg=error_msg,
        )
        db.add(log)
        db.commit()
    finally:
        db.close()


def track_embedding(
    user_id: str,
    session_id: str,
    model_name: str,
    model_type: str,
    node_type: str,
    input_tokens: int,
):
    """手动记录 DashScope SDK 调用（不走 LangChain callback）"""
    record_llm_call(
        user_id=user_id,
        session_id=session_id,
        model_name=model_name,
        model_type=model_type,
        node_type=node_type,
        input_tokens=input_tokens,
        output_tokens=0,
        latency_ms=0,
    )
