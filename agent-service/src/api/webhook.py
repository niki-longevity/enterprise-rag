"""MinIO webhook: 接收 bucket 事件通知，触发灰度更新"""
import json
import logging
from urllib.parse import unquote

from fastapi import APIRouter, Request, BackgroundTasks

from src.rag.gray_updater import handle_file_update, handle_file_delete

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/policy-update")
async def on_policy_update(request: Request, background_tasks: BackgroundTasks):
    """
    MinIO bucket notification webhook
    PUT 事件 → 灰度更新，DELETE 事件 → 直接删除
    """
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "invalid json"}, 400

    # MinIO S3 event 格式：Records[].s3.object.key（URL 编码，需解码）
    records = body.get("Records", [])
    if not records:
        key = body.get("Key")
        if key:
            records = [{"s3": {"object": {"key": key}}}]

    created_files = set()
    deleted_files = set()
    for record in records:
        event_name = record.get("eventName", "")
        key = unquote(record.get("s3", {}).get("object", {}).get("key", ""))

        if not key or not key.endswith(".md"):
            continue

        if "ObjectRemoved" in event_name:
            deleted_files.add(key)
        else:
            created_files.add(key)

        logger.info(f"MinIO 事件: {event_name} — {key}")

    for file_name in created_files:
        background_tasks.add_task(handle_file_update, file_name)
    for file_name in deleted_files:
        background_tasks.add_task(handle_file_delete, file_name)

    return {"status": "ok", "created": list(created_files), "deleted": list(deleted_files)}


@router.get("/webhook/health")
async def webhook_health():
    """webhook 健康检查"""
    return {"status": "ok"}
