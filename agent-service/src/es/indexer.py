"""
Elasticsearch 索引管理：创建索引、文档入库、删除索引
使用 ChromaDB 中已有的 chunk 数据，避免重复读取源文档
"""
from typing import List
from elasticsearch import Elasticsearch
from src.config.settings import settings as app_settings
from src.rag.retriever import get_all_chunks

# ES 连接（与 test.py 保持一致）
es = Elasticsearch(
    [f"http://{app_settings.es_host}:{app_settings.es_port}"],
    verify_certs=False,
)

INDEX_NAME = "policy_chunks"


def create_index():
    """创建 ES 索引（如果已存在则先删除重建）"""
    # 删除已存在的索引
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)

    # 创建索引 with mapping（使用 IK 中文分词器）
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "file_name": {"type": "keyword"},
                "chunk_idx": {"type": "integer"},
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"ES 索引 '{INDEX_NAME}' 创建成功")


def index_chunks():
    """
    从 ChromaDB 获取已有 chunk 并写入 ES
    避免重复读取源文档
    """
    chunks = get_all_chunks()
    print(f"从 ChromaDB 获取到 {len(chunks)} 个 chunk")

    # 批量写入 ES
    docs = []
    for chunk in chunks:
        docs.append({
            "index": {
                "_index": INDEX_NAME,
                "_id": chunk["id"]
            }
        })
        docs.append({
            "id": chunk["id"],
            "content": chunk["content"],
            "title": chunk["metadata"].get("title", ""),
            "file_name": chunk["metadata"].get("file_name", ""),
            "chunk_idx": chunk["metadata"].get("chunk_idx", 0),
        })

    if docs:
        es.bulk(body=docs)
        es.indices.refresh(index=INDEX_NAME)
        print(f"已写入 {len(chunks)} 个 chunk 到 ES 索引 '{INDEX_NAME}'")
    else:
        print("没有 chunk 可写入")


def delete_index():
    """删除 ES 索引"""
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"ES 索引 '{INDEX_NAME}' 已删除")
    else:
        print(f"ES 索引 '{INDEX_NAME}' 不存在")


if __name__ == "__main__":
    # create_index()
    # index_chunks()
    # 验证
    count = es.count(index=INDEX_NAME)["count"]
    print(f"\n验证: ES 索引中有 {count} 个文档")
