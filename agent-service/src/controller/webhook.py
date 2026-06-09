"""MinIO Webhook 路由

接收 MinIO bucket 的事件通知（PUT / DELETE），解析后交给 service 层处理灰度更新流水线。

事件流程：
  MinIO policies bucket 文件变更
    → POST /api/webhook/policy-update
    → 解析 S3 event 格式的 JSON body
    → 提取 created（新增/更新）和 deleted（删除）的文件列表
    → 后台任务调用 service/webhook.py → gray_updater 执行实际更新
"""

import json
import logging
from urllib.parse import unquote_plus

from fastapi import APIRouter, Request, BackgroundTasks

from src.service.webhook import process_policy_update

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/policy-update")
async def on_policy_update(request: Request, background_tasks: BackgroundTasks):
    """MinIO bucket 事件通知入口。

    解析 MinIO S3 event JSON，将 .md 文件变更分为 created / deleted 两组，
    交给后台任务异步执行灰度更新（不阻塞 webhook 响应）。
    """
    # ── 解析 JSON body ──────────────────────────────────────
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "invalid json"}, 400

    # MinIO 通知有两种格式：
    #   标准格式 → {"Records": [{...}, {...}]}
    #   简化格式 → {"Key": "xxx", "EventName": "s3:ObjectCreated:Put"}
    records = body.get("Records", [])
    if not records:
        key = body.get("Key")
        if key:
            records = [{"s3": {"object": {"key": key}}}]

    # ── 分类事件 ────────────────────────────────────────────
    created: dict[str, str] = {}   # file_name → etag（用于去重/校验）
    deleted: set[str] = set()

    for record in records:
        event_name = record.get("eventName", "")
        obj = record.get("s3", {}).get("object", {})
        key = unquote_plus(obj.get("key", ""))                # MinIO key 是 URL 编码的
        etag = obj.get("eTag", "") or obj.get("etag", "")     # MinIO 用驼峰命名 eTag

        # 只处理 .md 政策文档，忽略其他文件
        if not key or not key.endswith(".md"):
            continue

        if "ObjectRemoved" in event_name:
            deleted.add(key)
        else:
            created[key] = etag

        logger.info(f"MinIO 事件: {event_name} — {key}")

    # ── 后台异步处理 ────────────────────────────────────────
    # 不阻塞 webhook 响应，立刻返回 200，实际更新在后台执行
    background_tasks.add_task(process_policy_update, created, deleted)

    return {"status": "ok", "created": list(created.keys()), "deleted": list(deleted)}


@router.get("/webhook/health")
async def webhook_health():
    """Webhook 健康检查"""
    return {"status": "ok"}
