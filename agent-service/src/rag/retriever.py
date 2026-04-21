# 向量检索
# 使用LangChain + ChromaDB进行政策文档的向量存储和检索
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from src.config.settings import settings


class PolicyRetriever:
    """政策文档向量检索器"""

    def __init__(self):
        # 初始化LangChain Chroma向量存储
        self.vector_store = Chroma(
            collection_name="policies",
            embedding_function=DashScopeEmbeddings(
                model=settings.dashscope_embedding_model
            ),
            persist_directory=settings.chroma_db_path
        )

    def add_documents(self, chunks: List[dict]):
        """
        添加文档块到向量库
        Args:
            chunks: 文档块列表，格式: [{"title": "...", "content": "..."}]
        """
        # 转换为LangChain Document格式
        documents = [
            Document(
                page_content=chunk["content"],
                metadata={"title": chunk["title"]}
            )
            for chunk in chunks
        ]

        # 添加到向量库
        self.vector_store.add_documents(
            documents=documents,
            ids=[f"doc_{i}" for i in range(len(documents))]
        )

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """
        搜索相关文档
        Args:
            query: 用户问题
            top_k: 返回文档数
        Returns:
            文档列表，格式: [{"id": "...", "title": "...", "content": "..."}]
        """
        # 相似度搜索
        results = self.vector_store.similarity_search(
            query=query,
            k=top_k
        )

        # 格式化返回结果
        docs = []
        for i, doc in enumerate(results):
            docs.append({
                "id": f"doc_{i}",
                "title": doc.metadata.get("title", ""),
                "content": doc.page_content
            })
        return docs

    def clear(self):
        """清空向量库"""
        # 获取所有文档ID并删除
        existing_ids = self.vector_store.get()["ids"]
        if existing_ids:
            self.vector_store.delete(ids=existing_ids)


# 全局retriever实例
policy_retriever: Optional[PolicyRetriever] = None


def get_policy_retriever() -> PolicyRetriever:
    """获取全局retriever实例（单例）"""
    global policy_retriever
    if policy_retriever is None:
        policy_retriever = PolicyRetriever()
    return policy_retriever
