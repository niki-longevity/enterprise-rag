# Agent工具定义
from langchain_core.tools import tool
from src.rag.retriever import search


@tool
def search_policy(query: str) -> str:
    """搜索公司政策文档，回答用户关于政策、规定、制度的问题
    Args:
        query: 用户的问题，如"请假需要提前几天申请？"
    """
    print("提问：", query)
    docs = search(query, top_k=3)
    return docs

tools = [search_policy]
