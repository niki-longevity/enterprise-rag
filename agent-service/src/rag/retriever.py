# 向量检索
# 使用LlamaIndex + ChromaDB进行政策文档的向量存储和检索
from typing import List

import chromadb
from dashscope.rerank.text_rerank import TextReRank
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import TextNode
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.config.settings import settings as app_settings

# LlamaIndex 全局 embedding 配置
Settings.embed_model = DashScopeEmbedding(
    model_name=app_settings.dashscope_embedding_model
)

# ChromaDB 客户端
_chroma_client = chromadb.PersistentClient(path=app_settings.chroma_db_path)
_chroma_collection = _chroma_client.get_or_create_collection("policies")

# LlamaIndex vector store + index
_llama_vs = ChromaVectorStore(chroma_collection=_chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store=_llama_vs)


def add_documents(chunks: List[dict]):
    """
    添加文档块到向量库
    Args:
        chunks: 文档块列表，格式: [{"title": "...", "content": "..."}]
    """
    nodes = [
        TextNode(
            text=chunk["content"],
            metadata={
                "title": chunk["title"],
                "file_name": chunk["file_name"],
                "chunk_idx": chunk["chunk_idx"]
            },
            id_=f"{chunk['file_name']}::{chunk['chunk_idx']}"
        )
        for chunk in chunks
    ]
    index.insert_nodes(nodes)


def search(query: str, top_k: int = 5) -> List[dict]:
    """
    搜索相关文档（初检 top 15 → DashScope Rerank → 返回 top_k）
    Args:
        query: 用户问题
        top_k: 最终返回文档数
    Returns:
        文档列表，格式: [{"content": "...", "metadata": {"file_name": "...", "chunk_idx": 0, ...}}, ...]
    """
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(query)

    # 调用 DashScope qwen3-vl-rerank 精排
    doc_texts = [node.text for node in nodes]
    response = TextReRank.call(
        model="qwen3-vl-rerank",
        query=query,
        documents=doc_texts,
        top_n=top_k,
        api_key=app_settings.dashscope_api_key,
    )

    reranked = []
    for result in response.output.results:
        idx = result.index
        if idx < len(nodes):
            node = nodes[idx]
            reranked.append({
                "content": node.text,
                "metadata": node.metadata,
            })

    return reranked[:top_k]


def get_all_chunks() -> List[dict]:
    """获取全量chunk，返回 [{"id": ..., "content": ..., "metadata": {...}}, ...]"""
    results = _chroma_collection.get()
    return [
        {"id": id_, "content": content, "metadata": metadata}
        for id_, content, metadata in zip(
            results["ids"], results["documents"], results["metadatas"]
        )
    ]


def get_chunks_by_file(file_name: str) -> List[dict]:
    """获取指定文档的全量chunk"""
    results = _chroma_collection.get(where={"file_name": file_name})
    return [
        {"id": id_, "content": content, "metadata": metadata}
        for id_, content, metadata in zip(
            results["ids"], results["documents"], results["metadatas"]
        )
    ]


def clear():
    """清空向量库"""
    existing_ids = _chroma_collection.get()["ids"]
    if existing_ids:
        _chroma_collection.delete(ids=existing_ids)
