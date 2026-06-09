"""认证 API 路由 — 注册 / 登录

三层架构：controller 仅做参数校验和调用 service，所有业务逻辑（bcrypt 加密、
JWT 生成、DB 读写）都在 service/auth.py 中。
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.service.auth import register_user, login_user

router = APIRouter()


class AuthRequest(BaseModel):
    """注册 / 登录共用请求体"""
    username: str = Field(..., min_length=2, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


@router.post("/register")
def register(req: AuthRequest):
    """注册新用户 → 返回 JWT token"""
    return register_user(req.username, req.password)


@router.post("/login")
def login(req: AuthRequest):
    """登录验证 → 返回 JWT token，用户名或密码错误返回 401"""
    return login_user(req.username, req.password)
