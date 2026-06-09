"""Admin API 路由 — 角色配额管理 + LLM 成本追踪统计

路由分为两段：
  /admin/quota/*   → 管理员调整 user / vip 角色的 RPM / 日请求 / 日 Token 配额
  /admin/stats/*   → 仪表盘展示 LLM 调用量、成本、延迟等趋势数据
  /admin/pricing   → 返回各模型定价配置（JSON）
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.shared.quota_defaults import QUOTA_DEFAULTS
from src.service.quota import list_role_quotas, update_role_quota, reset_role_quota
from src.service import stats

router = APIRouter()


class RoleQuotaRequest(BaseModel):
    """角色配额修改请求，三项均为必填且 >= 1"""
    daily_requests: int = Field(..., ge=1, description="每日请求上限")
    daily_tokens: int = Field(..., ge=1, description="每日 Token 上限")
    rpm_requests: int = Field(..., ge=1, description="每分钟请求上限")


# ── 角色配额管理 ──────────────────────────────────────────────

@router.get("/quota/roles")
def get_quota_roles():
    """列出所有角色的当前配额配置（含默认值和自定义覆盖值）"""
    return list_role_quotas()


@router.put("/quota/roles/{role}")
def put_role_quota(role: str, req: RoleQuotaRequest):
    """更新指定角色的配额 → 写入 DB 并刷新 Redis 缓存"""
    if role not in QUOTA_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"无效角色: {role}")
    update_role_quota(role, req.daily_requests, req.daily_tokens, req.rpm_requests)
    return {"status": "ok"}


@router.delete("/quota/roles/{role}")
def delete_role_quota(role: str):
    """重置指定角色的配额为默认值 → 删除 DB 自定义记录 + 刷新 Redis"""
    if role not in QUOTA_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"无效角色: {role}")
    reset_role_quota(role)
    return {"status": "ok"}


# ── LLM 成本追踪统计 ──────────────────────────────────────────

@router.get("/stats/overview")
def get_stats_overview(
    from_: str | None = Query(None, alias="from", description="起始日期，格式 YYYY-MM-DD"),
    to: str | None = Query(None, description="截止日期，格式 YYYY-MM-DD，默认今天"),
):
    """时段总览：活跃用户数、会话数、总调用次数、总成本、错误数、平均延迟"""
    return stats.get_overview(from_, to)


@router.get("/stats/trend")
def get_stats_trend(
    from_: str | None = Query(None, alias="from", description="起始日期"),
    to: str | None = Query(None, description="截止日期"),
):
    """每日趋势：按日期 + 模型类型聚合的调用量、Token、成本、延迟"""
    return stats.get_trend(from_, to)


@router.get("/stats/trend-hourly")
def get_stats_trend_hourly():
    """小时趋势：过去 24 小时每小时的调用量、Token、成本、延迟"""
    return stats.get_trend_hourly()


@router.get("/stats/aggregation")
def get_stats_aggregation(
    from_: str | None = Query(None, alias="from", description="起始日期"),
    to: str | None = Query(None, description="截止日期"),
):
    """时段聚合：每用户 / 每会话的平均调用次数、Token 用量、成本、延迟"""
    return stats.get_aggregation(from_, to)


@router.get("/pricing")
def get_pricing():
    """返回各模型定价配置（从 pricing.json 读取）"""
    path = Path(__file__).parent.parent / "shared" / "tracking" / "pricing.json"
    return json.loads(path.read_text(encoding="utf-8"))
