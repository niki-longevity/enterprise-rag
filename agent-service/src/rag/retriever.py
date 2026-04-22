# 向量检索
# 使用LangChain + ChromaDB进行政策文档的向量存储和检索
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from src.config.settings import settings


vector_store = Chroma(
    collection_name="policies",
    embedding_function=DashScopeEmbeddings(
        model=settings.dashscope_embedding_model
    ),
    persist_directory=settings.chroma_db_path
)

def add_documents(chunks: List[dict]):
    """
    添加文档块到向量库
    Args:
        chunks: 文档块列表，格式: [{"title": "...", "content": "..."}]
    """
    # 转换为LangChain Document格式
    documents = [
        Document(
            page_content=chunk["content"],
            metadata={
                "title": chunk["title"],
                "file_name": chunk["file_name"],
                "chunk_idx": chunk["chunk_idx"]
            }
        )
        for chunk in chunks
    ]

    # 添加到向量库
    vector_store.add_documents(
        documents=documents,
        ids=[f"{chunk['file_name']}::{chunk['chunk_idx']}" for chunk in chunks]
    )

def search(query: str, top_k: int = 3) -> str:
    """
    搜索相关文档
    Args:
        query: 用户问题
        top_k: 返回文档数
    Returns:
        文档列表，格式: [{"id": "...", "title": "...", "content": "..."}]
    """
    # 相似度搜索
    results = vector_store.similarity_search(
        query,
        top_k
    )
    context = "\n".join([doc.page_content for doc in results])

    return context

def clear():
    """清空向量库"""
    # 获取所有文档ID并删除
    existing_ids = vector_store.get()["ids"]
    if existing_ids:
        vector_store.delete(ids=existing_ids)