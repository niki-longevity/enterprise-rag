# 向量检索
# 使用ChromaDB进行政策文档的向量存储和检索
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional
from src.config.settings import settings


class PolicyRetriever:
    # 政策文档向量检索器

    def __init__(self):
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)

        # 使用Sentence-Transformers生成向量
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # 获取或创建policy集合
        self.collection = self.client.get_or_create_collection(
            name="policies",
            embedding_function=self.ef
        )

    def add_documents(self, chunks: List[dict]):
        # 添加文档块到向量库
        # chunks格式: [{"title": "...", "content": "..."}]
        ids = [f"doc_{i}" for i in range(len(chunks))]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [{"title": chunk["title"]} for chunk in chunks]
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        # 搜索相关文档
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        # 格式化返回结果
        docs = []
        for i in range(len(results["ids"][0])):
            docs.append({
                "id": results["ids"][0][i],
                "title": results["metadatas"][0][i]["title"],
                "content": results["documents"][0][i]
            })
        return docs

    def clear(self):
        # 清空向量库
        self.client.delete_collection("policies")
        self.collection = self.client.create_collection(
            name="policies",
            embedding_function=self.ef
        )


# 全局retriever实例
policy_retriever: Optional[PolicyRetriever] = None


def get_policy_retriever() -> PolicyRetriever:
    # 获取全局retriever实例（单例）
    global policy_retriever
    if policy_retriever is None:
        policy_retriever = PolicyRetriever()
    return policy_retriever
