# 认证API路由 - 注册/登录
import datetime
import jwt
from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from pydantic import BaseModel, Field

from src.db.session import SessionLocal
from src.db.models import User
from src.db.mapper import BaseMapper
from src.config.settings import settings

router = APIRouter()


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6, max_length=50)


def _create_token(user: User) -> str:
    """生成 JWT，有效期 7 天"""
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=settings.jwt_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register")
def register(req: AuthRequest):
    """注册新用户，返回 JWT token"""
    db = SessionLocal()
    try:
        mapper = BaseMapper(User, db)
        existing = mapper.list_by_field("username", req.username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")

        user = User(
            username=req.username,
            password_hash=bcrypt.hash(req.password),
        )
        mapper.save(user)
        return {"token": _create_token(user)}
    finally:
        db.close()


@router.post("/login")
def login(req: AuthRequest):
    """登录，返回 JWT token"""
    db = SessionLocal()
    try:
        mapper = BaseMapper(User, db)
        users = mapper.list_by_field("username", req.username)
        if not users or not bcrypt.verify(req.password, users[0].password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {"token": _create_token(users[0])}
    finally:
        db.close()
