# 资源查询工具
from typing import List, Optional
from src.client.java_client import get_java_client


def query_resource(
    resource_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[dict]:
    """
    查询资源

    Args:
        resource_type: 资源类型 (PROJECTOR, LAPTOP, ROOM, LICENSE)
        status: 资源状态 (AVAILABLE, IN_USE, MAINTENANCE)

    Returns:
        资源列表
    """
    client = get_java_client()
    return client.query_resources(resource_type=resource_type, status=status)


def query_available_resources() -> List[dict]:
    """
    查询所有可用资源

    Returns:
        可用资源列表
    """
    return query_resource(status="AVAILABLE")
