# 向量检索
from typing import List
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from src.config.settings import settings


def get_vector_store():
    """获取Chroma向量存储实例"""
    return Chroma(
        collection_name="policies",
        embedding_function=DashScopeEmbeddings(
            model=settings.dashscope_embedding_model
        ),
        persist_directory=settings.chroma_db_path
    )


def add_documents(chunks: List[dict]):
    """添加文档块到向量库"""
    vector_store = get_vector_store()

    documents = [
        Document(
            page_content=chunk["content"],
            metadata={"title": chunk["title"]}
        )
        for chunk in chunks
    ]

    vector_store.add_documents(
        documents=documents,
        ids=[f"doc_{i}" for i in range(len(documents))]
    )


def search_policy(query: str, top_k: int = 3) -> str:
    """搜索相关文档，返回拼接的上下文"""
    vector_store = get_vector_store()

    print(f"[搜索问题]:\n{query}")
    results = vector_store.similarity_search(query, k=top_k)
    context = "\n".join([doc.page_content for doc in results])
    print(f"[搜索结果]:\n{context}")

    return context


def clear_vector_store():
    """清空向量库"""
    vector_store = get_vector_store()
    existing_ids = vector_store.get()["ids"]
    if existing_ids:
        vector_store.delete(ids=existing_ids)
