# Admin API — 配额管理 + 成本追踪统计端点
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func as sa_func

from src.db.session import SessionLocal
from src.db.models import User, RoleQuotaConfig, LLMCallLog
from src.db.mapper import BaseMapper
from src.db.session import engine
from src.config.client import redis_client
from src.auth.quota_defaults import QUOTA_DEFAULTS
from sqlalchemy import text

router = APIRouter()


class RoleQuotaRequest(BaseModel):
    daily_requests: int = Field(..., ge=1)
    daily_tokens: int = Field(..., ge=1)
    rpm_requests: int = Field(..., ge=1)


# ── 角色配额管理 ──────────────────────────────────────────

@router.get("/quota/roles")
def list_role_quotas():
    """列出所有角色的配额配置"""
    db = SessionLocal()
    try:
        mapper = BaseMapper(RoleQuotaConfig, db)
        configs = mapper.list_all()
        result = {}
        for role, defaults in QUOTA_DEFAULTS.items():
            entry = {"role": role, "daily_requests": defaults["daily_requests"],
                     "daily_tokens": defaults["daily_tokens"], "rpm_requests": defaults["rpm_requests"],
                     "source": "default"}
            for c in configs:
                if c.role == role:
                    entry["daily_requests"] = c.daily_requests
                    entry["daily_tokens"] = c.daily_tokens
                    entry["rpm_requests"] = c.rpm_requests
                    entry["source"] = "custom"
                    break
            result[role] = entry
        return result
    finally:
        db.close()


@router.put("/quota/roles/{role}")
def update_role_quota(role: str, req: RoleQuotaRequest):
    """更新角色配额（写 DB + 更新 Redis）"""
    if role not in QUOTA_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"无效角色: {role}")

    db = SessionLocal()
    try:
        mapper = BaseMapper(RoleQuotaConfig, db)
        configs = mapper.list_by_field("role", role)
        if configs:
            c = configs[0]
            c.daily_requests = req.daily_requests
            c.daily_tokens = req.daily_tokens
            c.rpm_requests = req.rpm_requests
            db.commit()
        else:
            mapper.save(RoleQuotaConfig(
                role=role,
                daily_requests=req.daily_requests,
                daily_tokens=req.daily_tokens,
                rpm_requests=req.rpm_requests,
            ))
    finally:
        db.close()

    # 同步到 Redis
    redis_client.set(f"quota:config:{role}", json.dumps({
        "daily_requests": req.daily_requests,
        "daily_tokens": req.daily_tokens,
        "rpm_requests": req.rpm_requests,
    }))
    return {"status": "ok"}


@router.delete("/quota/roles/{role}")
def reset_role_quota(role: str):
    """重置角色配额为默认值"""
    if role not in QUOTA_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"无效角色: {role}")

    db = SessionLocal()
    try:
        mapper = BaseMapper(RoleQuotaConfig, db)
        configs = mapper.list_by_field("role", role)
        if configs:
            db.delete(configs[0])
            db.commit()
    finally:
        db.close()

    # Redis 恢复默认
    defaults = QUOTA_DEFAULTS[role]
    redis_client.set(f"quota:config:{role}", json.dumps(dict(defaults)))
    return {"status": "ok"}


# ── 成本追踪统计端点 ──────────────────────────────────────────

def _parse_date_range(from_: str | None, to_: str | None) -> tuple[date, date]:
    """解析日期范围，默认最近 7 天"""
    if to_:
        end = datetime.strptime(to_, "%Y-%m-%d").date()
    else:
        end = date.today()
    if from_:
        start = datetime.strptime(from_, "%Y-%m-%d").date()
    else:
        start = end - timedelta(days=6)
    return start, end


@router.get("/stats/overview")
def stats_overview(from_: str | None = Query(None, alias="from"), to: str | None = None):
    """时段总览：活跃用户/会话/总调用/总成本"""
    start, end = _parse_date_range(from_, to)
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT
                COUNT(DISTINCT user_id) AS active_users,
                COUNT(DISTINCT session_id) AS active_sessions,
                COUNT(*) AS total_calls,
                COALESCE(SUM(cost), 0) AS total_cost,
                COALESCE(SUM(input_tokens), 0) AS total_input,
                COALESCE(SUM(output_tokens), 0) AS total_output,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS error_count
            FROM llm_call_logs
            WHERE created_at >= :start AND created_at < :end2
        """), {"start": start, "end2": end + timedelta(days=1)}).fetchone()
        return {
            "active_users": r[0], "active_sessions": r[1],
            "total_calls": r[2], "total_cost": round(float(r[3]), 4),
            "total_input_tokens": r[4], "total_output_tokens": r[5],
            "error_count": r[6],
        }


@router.get("/stats/trend")
def stats_trend(from_: str | None = Query(None, alias="from"), to: str | None = None):
    """每日趋势：按日期 + 模型类型聚合"""
    start, end = _parse_date_range(from_, to)
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT DATE(created_at) AS d, model_type,
                   COUNT(*) AS calls,
                   COALESCE(SUM(input_tokens), 0) AS itok,
                   COALESCE(SUM(output_tokens), 0) AS otok,
                   COALESCE(SUM(cost), 0) AS cost,
                   COUNT(DISTINCT user_id) AS users,
                   COUNT(DISTINCT session_id) AS sessions
            FROM llm_call_logs
            WHERE created_at >= :start AND created_at < :end2
            GROUP BY d, model_type
            ORDER BY d
        """), {"start": start, "end2": end + timedelta(days=1)}).fetchall()

        days = {}
        for row in rows:
            d = str(row[0])
            if d not in days:
                days[d] = {"date": d, "models": {}, "active_users": 0, "active_sessions": 0}
            days[d]["models"][row[1]] = {
                "calls": row[2], "input_tokens": row[3],
                "output_tokens": row[4], "cost": round(float(row[5]), 4),
            }
            days[d]["active_users"] = max(days[d]["active_users"], row[6])
            days[d]["active_sessions"] = max(days[d]["active_sessions"], row[7])

        return {"days": list(days.values())}


@router.get("/stats/trend-hourly")
def stats_trend_hourly():
    """小时趋势：过去 24h 按小时 + 模型类型聚合"""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT DATE_FORMAT(created_at, '%Y-%m-%d %H:00') AS h, model_type,
                   COUNT(*) AS calls,
                   COALESCE(SUM(input_tokens), 0) AS itok,
                   COALESCE(SUM(output_tokens), 0) AS otok,
                   COALESCE(SUM(cost), 0) AS cost
            FROM llm_call_logs
            WHERE created_at >= NOW() - INTERVAL 24 HOUR
            GROUP BY h, model_type
            ORDER BY h
        """)).fetchall()

        hours = {}
        for row in rows:
            h = row[0]
            if h not in hours:
                hours[h] = {"hour": h, "models": {}}
            hours[h]["models"][row[1]] = {
                "calls": row[2], "input_tokens": row[3],
                "output_tokens": row[4], "cost": round(float(row[5]), 4),
            }

        return {"hours": list(hours.values())}


@router.get("/stats/aggregation")
def stats_aggregation(from_: str | None = Query(None, alias="from"), to: str | None = None):
    """时段聚合：每用户/每会话平均"""
    start, end = _parse_date_range(from_, to)
    with engine.connect() as conn:
        # 每用户平均
        u = conn.execute(text("""
            SELECT AVG(calls), AVG(itok), AVG(otok), AVG(cost)
            FROM (
                SELECT user_id,
                       COUNT(*) AS calls,
                       COALESCE(SUM(input_tokens), 0) AS itok,
                       COALESCE(SUM(output_tokens), 0) AS otok,
                       COALESCE(SUM(cost), 0) AS cost
                FROM llm_call_logs
                WHERE created_at >= :start AND created_at < :end2
                GROUP BY user_id
            ) t
        """), {"start": start, "end2": end + timedelta(days=1)}).fetchone()

        # 每会话平均
        s = conn.execute(text("""
            SELECT AVG(calls), AVG(itok), AVG(otok), AVG(cost)
            FROM (
                SELECT session_id,
                       COUNT(*) AS calls,
                       COALESCE(SUM(input_tokens), 0) AS itok,
                       COALESCE(SUM(output_tokens), 0) AS otok,
                       COALESCE(SUM(cost), 0) AS cost
                FROM llm_call_logs
                WHERE created_at >= :start AND created_at < :end2
                GROUP BY session_id
            ) t
        """), {"start": start, "end2": end + timedelta(days=1)}).fetchone()

        return {
            "per_user": {
                "avg_calls": round(float(u[0] or 0), 1),
                "avg_input_tokens": int(u[1] or 0),
                "avg_output_tokens": int(u[2] or 0),
                "avg_cost": round(float(u[3] or 0), 4),
            },
            "per_session": {
                "avg_calls": round(float(s[0] or 0), 1),
                "avg_input_tokens": int(s[1] or 0),
                "avg_output_tokens": int(s[2] or 0),
                "avg_cost": round(float(s[3] or 0), 4),
            },
        }


@router.get("/pricing")
def get_pricing():
    """模型定价配置"""
    path = Path(__file__).parent.parent / "tracking" / "pricing.json"
    return json.loads(path.read_text(encoding="utf-8"))
