# Admin API — 配额管理端点
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.db.session import SessionLocal
from src.db.models import User, UserQuotaOverride
from src.db.mapper import BaseMapper

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
