# 配额控制 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于用户分层的请求频率、日请求数、Token 上限的硬拦截（429），管理员可手动覆盖。

**Architecture:** `get_current_user → check_quota(Depends) → handler`。check_quota 用 Redis 计数器实现 RPM/日请求/日 Token 三层限流，MySQL user_quota_overrides 表支持管理员按用户调额。

**Tech Stack:** Redis (INCR + TTL), MySQL, FastAPI Depends

---

### Task 1: 数据模型 — users 加 role + UserQuotaOverride

**Files:**
- Modify: `agent-service/src/db/models.py`

- [ ] **Step 1: User 模型加 role 字段**

```python
class User(Base):
    """用户实体"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # ← 新增
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 2: 追加 UserQuotaOverride 模型**

在 User 类之后追加：

```python
class UserQuotaOverride(Base):
    """用户配额覆盖"""
    __tablename__ = "user_quota_overrides"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True)
    daily_requests = Column(Integer, nullable=True)
    daily_tokens = Column(Integer, nullable=True)
    rpm_requests = Column(Integer, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 3: ALTER + CREATE TABLE**

```bash
"C:/Users/15219/.conda/envs/pytorch/python.exe" -c "
import sys; sys.path.insert(0, 'D:/Project/employee_assistant_Agent/agent-service')
from src.db.session import engine
from src.db.models import Base, User, UserQuotaOverride
# 创建新表
Base.metadata.create_all(bind=engine)
print('ok')
"
```

注意：MySQL 不支持 ALTER TABLE ADD COLUMN IF NOT EXISTS，所以如果 users 表已有数据但无 role 列需手动 ALTER：

```sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';
```

- [ ] **Step 4: Commit**

```bash
git add agent-service/src/db/models.py && git commit -m "数据模型：users 加 role 字段 + UserQuotaOverride 表"
```

---

### Task 2: 配额默认值常量

**Files:**
- Create: `agent-service/src/auth/quota_defaults.py`

- [ ] **Step 1: 创建 quota_defaults.py**

```python
# 角色默认配额
QUOTA_DEFAULTS = {
    "user": {
        "daily_requests": 100,
        "daily_tokens": 200_000,
        "rpm_requests": 10,
    },
    "vip": {
        "daily_requests": 500,
        "daily_tokens": 1_000_000,
        "rpm_requests": 30,
    },
}
```

- [ ] **Step 2: Commit**

```bash
git add agent-service/src/auth/quota_defaults.py && git commit -m "新增配额默认值配置"
```

---

### Task 3: check_quota Depends

**Files:**
- Create: `agent-service/src/auth/quota.py`

- [ ] **Step 1: 创建 quota.py**

```python
# 配额检查 Depends — RPM / 日请求数 / 日 Token 三层限流
from datetime import date
from fastapi import HTTPException, Depends

from src.auth.deps import get_current_user
from src.auth.quota_defaults import QUOTA_DEFAULTS
from src.config.client import redis_client
from src.db.session import SessionLocal
from src.db.models import User, UserQuotaOverride
from src.db.mapper import BaseMapper


def _get_effective_quota(user_id: str) -> dict:
    """返回用户生效的配额阈值"""
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
        # TTL 到次日 00:00
        from datetime import datetime, timedelta
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

    # 返回配额信息（供 handler 和前端使用）
    return {
        "role": quota.get("_role", "user"),
        "daily_requests_limit": quota["daily_requests"],
        "daily_requests_used": req_count,
        "daily_tokens_limit": quota["daily_tokens"],
        "daily_tokens_used": tok_used,
        "rpm_limit": quota["rpm_requests"],
    }
```

- [ ] **Step 2: 修复 _get_effective_quota 返回 role 标记**

在 `check_quota` 返回的 dict 中补充 role，修改 `_get_effective_quota` 返回值加 `_role`：

```python
return {
    "_role": role,
    "daily_requests": ...,
    "daily_tokens": ...,
    "rpm_requests": ...,
}
```

- [ ] **Step 3: Commit**

```bash
git add agent-service/src/auth/quota.py && git commit -m "新增 check_quota 三层限流 Depends"
```

---

### Task 4: chat.py 加入 Depends(check_quota)

**Files:**
- Modify: `agent-service/src/api/chat.py`

- [ ] **Step 1: 导入 check_quota**

在 import 区域追加：

```python
from src.auth.quota import check_quota
```

- [ ] **Step 2: /chat 路由加 Depends**

```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    quota_info: dict = Depends(check_quota),
    db: Session = Depends(get_db)
):
    """流式对话接口"""
    return await chat_stream_impl(user_id, request.message, request.sessionId, db)
```

- [ ] **Step 3: Commit**

```bash
git add agent-service/src/api/chat.py && git commit -m "chat 路由加入配额检查"
```

---

### Task 5: Admin 配额管理端点

**Files:**
- Create: `agent-service/src/api/admin.py`

- [ ] **Step 1: 创建 admin.py**

```python
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
```

- [ ] **Step 2: main.py 注册 admin 路由**

```python
from src.api import chat, webhook, auth, admin

app.include_router(admin.router, prefix="/admin", tags=["admin"])
```

- [ ] **Step 3: Commit**

```bash
git add agent-service/src/api/admin.py agent-service/src/main.py && git commit -m "新增 admin 配额管理端点"
```

---

### Task 6: 端到端验证

- [ ] **Step 1: 启动后端并测试**

```bash
"C:/Users/15219/.conda/envs/pytorch/python.exe" -c "
import sys
sys.path.insert(0, 'D:/Project/employee_assistant_Agent/agent-service')
from src.main import app
from fastapi.testclient import TestClient

c = TestClient(app)

# 注册 + 登录
r = c.post('/api/register', json={'username': 'qtest', 'password': '123456'})
token = r.json()['token']

# 快速发 11 次请求 (RPM 默认 10)
for i in range(11):
    r = c.post('/api/chat', json={'message': 'hi'}, headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 429:
        print(f'  RPM 限流触发于第 {i+1} 次 → 429: {r.json()[\"detail\"]}')
        break
    else:
        print(f'  #{i+1} → {r.status_code}')

# 测试日请求数限流
import time
time.sleep(61)  # 等 RPM 窗口过期

# 快速发 101 次
blocked = 0
for i in range(101):
    r = c.post('/api/chat', json={'message': 'x'}, headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 429:
        blocked += 1
        if blocked == 1:
            print(f'  日请求限流触发 → 429: {r.json()[\"detail\"]}')
print(f'  共 {blocked} 次被拦截')

# Admin 端点测试
r = c.get('/admin/users/1/quota')
print(f'  GET quota → {r.status_code}: {r.json()}')

r = c.put('/admin/users/1/quota', json={'daily_requests': 999})
print(f'  PUT quota → {r.status_code}: {r.json()}')

r = c.delete('/admin/users/1/quota')
print(f'  DELETE quota → {r.status_code}: {r.json()}')

print('quota 模块验证通过')
"
```

Expected:
- 第 11 次请求返回 429（RPM 限流）
- 等待 61 秒后再发 101 次，应有部分被 429 拦截
- Admin GET/PUT/DELETE 正常工作

- [ ] **Step 2: Commit（如有修正确认提交）**
