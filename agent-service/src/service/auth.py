"""认证服务：注册、登录、JWT 令牌生成"""
import datetime
import bcrypt
import jwt
from fastapi import HTTPException
from src.dao.session import SessionLocal
from src.model.models import User
from src.dao.mapper import BaseMapper
from src.shared.config import settings


def _create_token(user: User) -> str:
    """生成 JWT，有效期由配置决定"""
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=settings.jwt_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def register_user(username: str, password: str) -> dict:
    """注册新用户，返回 JWT token"""
    db = SessionLocal()
    try:
        mapper = BaseMapper(User, db)
        existing = mapper.list_by_field("username", username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")

        user = User(
            username=username,
            password_hash=bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8'),
        )
        mapper.save(user)
        return {"token": _create_token(user)}
    finally:
        db.close()


def login_user(username: str, password: str) -> dict:
    """登录验证，返回 JWT token"""
    db = SessionLocal()
    try:
        mapper = BaseMapper(User, db)
        users = mapper.list_by_field("username", username)
        if not users or not bcrypt.checkpw(
            password.encode('utf-8'),
            users[0].password_hash.encode('utf-8')
        ):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {"token": _create_token(users[0])}
    finally:
        db.close()
