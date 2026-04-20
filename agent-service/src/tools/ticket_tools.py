# 工单工具
from typing import Optional, Dict, Any
from src.client.java_client import get_java_client


def create_ticket(
    user_id: str,
    ticket_type: str,
    reason: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    创建工单

    Args:
        user_id: 用户ID
        ticket_type: 工单类型 (BORROW, LEAVE, EXPENSE, etc.)
        reason: 申请原因
        metadata: 扩展信息

    Returns:
        创建的工单信息
    """
    client = get_java_client()
    return client.create_ticket(user_id, ticket_type, reason, metadata)


def get_ticket(ticket_no: str) -> Optional[Dict[str, Any]]:
    """
    查询工单

    Args:
        ticket_no: 工单号

    Returns:
        工单信息
    """
    client = get_java_client()
    return client.get_ticket(ticket_no)
