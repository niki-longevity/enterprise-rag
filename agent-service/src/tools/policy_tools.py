# 政策文档工具
from typing import List
from src.rag.retriever import get_policy_retriever


def search_policy(query: str, top_k: int = 3) -> str:
    """
    搜索政策文档

    Args:
        query: 用户查询
        top_k: 返回的最相关文档数量

    Returns:
        相关文档列表，每个文档包含 id, title, content
    """
    print("提问：",query)
    retriever = get_policy_retriever()
    return retriever.search(query, top_k)
