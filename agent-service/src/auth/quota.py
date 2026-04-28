# 配额检查 Depends — RPM / 日请求数 / 日 Token 三层限流
from datetime import date, datetime, timedelta
from fastapi import HTTPException, Depends

from src.auth.deps import get_current_user
from src.auth.quota_defaults import QUOTA_DEFAULTS
from src.config.client import redis_client
from src.db.session import SessionLocal
from src.db.models import User, UserQuotaOverride
from src.db.mapper import BaseMapper


def _get_effective_quota(user_id: str) -> dict:
    """返回用户生效的配额阈值 + _role 标记"""
    db = SessionLocal()
    try:
        user_mapper = BaseMapper(User, db)
        user = user_mapper.get_by_id(int(user_id))
        role = user.role if user else "user"

        defaults = QUOTA_DEFAULTS.get(role, QUOTA_DEFAULTS["user"])

        override_mapper = BaseMapper(UserQuotaOverride, db)
        overrides = override_mapper.list_by_field("user_id", int(user_id))
        override = overrides[0] if overrides else None

        return {
            "_role": role,
            "daily_requests": override.daily_requests if override and override.daily_requests is not None else defaults["daily_requests"],
            "daily_tokens": override.daily_tokens if override and override.daily_tokens is not None else defaults["daily_tokens"],
            "rpm_requests": override.rpm_requests if override and override.rpm_requests is not None else defaults["rpm_requests"],
        }
    finally:
        db.close()


async def check_quota(user_id: str = Depends(get_current_user)) -> dict:
    """检查用户配额，超额返回 429"""
    quota = _get_effective_quota(user_id)
    today = date.today().isoformat()

    # 1. RPM 检查
    rpm_key = f"ratelimit:rpm:{user_id}"
    rpm_count = redis_client.incr(rpm_key)
    if rpm_count == 1:
        redis_client.expire(rpm_key, 60)
    if rpm_count > quota["rpm_requests"]:
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，每分钟最多 {quota['rpm_requests']} 次",
        )

    # 2. 日请求数检查
    req_key = f"quota:daily:req:{user_id}:{today}"
    req_count = redis_client.incr(req_key)
    if req_count == 1:
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        redis_client.expireat(req_key, tomorrow)
    if req_count > quota["daily_requests"]:
        raise HTTPException(
            status_code=429,
            detail=f"今日请求次数已用完（上限 {quota['daily_requests']} 次）",
        )

    # 3. 日 Token 检查
    tok_key = f"quota:daily:tok:{user_id}:{today}"
    tok_used = int(redis_client.get(tok_key) or 0)
    if tok_used >= quota["daily_tokens"]:
        raise HTTPException(
            status_code=429,
            detail=f"今日 Token 额度已用完（上限 {quota['daily_tokens']}）",
        )

    return {
        "role": quota["_role"],
        "daily_requests_limit": quota["daily_requests"],
        "daily_requests_used": req_count,
        "daily_tokens_limit": quota["daily_tokens"],
        "daily_tokens_used": tok_used,
        "rpm_limit": quota["rpm_requests"],
    }
