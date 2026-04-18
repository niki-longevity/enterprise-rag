# Java客户端
# 调用Java服务的内部API接口
import httpx
from typing import List, Optional, Dict, Any
from src.config.settings import settings


class JavaServiceClient:
    # Java服务HTTP客户端

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.java_service_url
        self.client = httpx.Client(timeout=5.0)

    def close(self):
        # 关闭HTTP客户端
        self.client.close()

    def search_policies(self, keyword: str) -> List[Dict[str, Any]]:
        # 搜索政策文档
        # GET /api/internal/policies/search?keyword=xxx
        url = f"{self.base_url}/api/internal/policies/search"
        params = {"keyword": keyword}
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("policies", [])

    def query_resources(
        self,
        resource_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # 查询资源
        # GET /api/internal/resources?type=xxx&status=xxx
        url = f"{self.base_url}/api/internal/resources"
        params = {}
        if resource_type:
            params["type"] = resource_type
        if status:
            params["status"] = status
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("resources", [])

    def create_ticket(
        self,
        user_id: str,
        ticket_type: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 创建工单
        # POST /api/internal/tickets
        url = f"{self.base_url}/api/internal/tickets"
        body = {
            "userId": user_id,
            "type": ticket_type,
            "reason": reason
        }
        if metadata:
            body["metadata"] = metadata
        resp = self.client.post(url, json=body)
        resp.raise_for_status()
        return resp.json()

    def get_ticket(self, ticket_no: str) -> Optional[Dict[str, Any]]:
        # 根据工单号查询工单
        # GET /api/internal/tickets/no/{ticketNo}
        url = f"{self.base_url}/api/internal/tickets/no/{ticket_no}"
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.json()


# 全局Java客户端实例
_java_client: Optional[JavaServiceClient] = None


def get_java_client() -> JavaServiceClient:
    # 获取全局Java客户端实例（单例）
    global _java_client
    if _java_client is None:
        _java_client = JavaServiceClient()
    return _java_client
