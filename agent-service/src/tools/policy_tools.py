# 政策文档工具
from src.rag.retriever import search_policy as _search_policy


def search_policy(query: str, top_k: int = 3) -> str:
    """搜索政策文档"""
    print("提问：", query)
    return _search_policy(query, top_k)
