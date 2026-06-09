"""Webhook 服务：接收 MinIO 事件，协调灰度更新流水线"""
from src.infrastructure.search.gray_updater import handle_file_update, handle_file_delete


def process_policy_update(created: dict[str, str], deleted: set[str]):
    """处理 MinIO webhook 事件，分发到灰度更新流水线

    Args:
        created: {file_name: etag} 新建或更新的文件
        deleted: 被删除的文件名集合
    """
    for file_name, etag in created.items():
        handle_file_update(file_name, etag)
    for file_name in deleted:
        handle_file_delete(file_name)
