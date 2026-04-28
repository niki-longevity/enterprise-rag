# Admin API — 配额管理 + 成本追踪统计端点
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func as sa_func

from src.db.session import SessionLocal
from src.db.models import User, UserQuotaOverride, LLMCallLog
from src.db.mapper import BaseMapper
from src.db.session import engine
from sqlalchemy import text

router = APIRouter()


class QuotaOverrideRequest(BaseModel):
    daily_requests: int | None = Field(None, ge=0)
    daily_tokens: int | None = Field(None, ge=0)
    rpm_requests: int | None = Field(None, ge=0)


@router.get("/users/{user_id}/quota")
def get_user_quota(user_id: int):
    """查看用户配额覆盖和当前用量"""
    db = SessionLocal()
    try:
        user_mapper = BaseMapper(User, db)
        user = user_mapper.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        override_mapper = BaseMapper(UserQuotaOverride, db)
        overrides = override_mapper.list_by_field("user_id", user_id)
        override = overrides[0] if overrides else None

        return {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
            "override": {
                "daily_requests": override.daily_requests,
                "daily_tokens": override.daily_tokens,
                "rpm_requests": override.rpm_requests,
            } if override else None,
        }
    finally:
        db.close()


@router.put("/users/{user_id}/quota")
def set_user_quota(user_id: int, req: QuotaOverrideRequest):
    """设置用户配额覆盖"""
    db = SessionLocal()
    try:
        user_mapper = BaseMapper(User, db)
        if not user_mapper.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="用户不存在")

        override_mapper = BaseMapper(UserQuotaOverride, db)
        overrides = override_mapper.list_by_field("user_id", user_id)

        if overrides:
            override = overrides[0]
            if req.daily_requests is not None:
                override.daily_requests = req.daily_requests
            if req.daily_tokens is not None:
                override.daily_tokens = req.daily_tokens
            if req.rpm_requests is not None:
                override.rpm_requests = req.rpm_requests
            db.commit()
        else:
            override = UserQuotaOverride(
                user_id=user_id,
                daily_requests=req.daily_requests,
                daily_tokens=req.daily_tokens,
                rpm_requests=req.rpm_requests,
            )
            override_mapper.save(override)

        return {"status": "ok"}
    finally:
        db.close()


@router.delete("/users/{user_id}/quota")
def delete_user_quota(user_id: int):
    """删除用户配额覆盖，恢复默认"""
    db = SessionLocal()
    try:
        override_mapper = BaseMapper(UserQuotaOverride, db)
        overrides = override_mapper.list_by_field("user_id", user_id)
        if overrides:
            db.delete(overrides[0])
            db.commit()
        return {"status": "ok"}
    finally:
        db.close()


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
