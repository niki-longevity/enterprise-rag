"""
Elasticsearch BM25 关键词检索
返回格式与向量检索保持一致，便于多路召回融合
"""
from typing import List
from elasticsearch import Elasticsearch
from src.config.settings import settings as app_settings

# ES 连接（与 test.py 保持一致）
es = Elasticsearch(
    [f"http://{app_settings.es_host}:{app_settings.es_port}"],
    verify_certs=False,
)

INDEX_NAME = "policy_chunks"


def bm25_search(query: str, top_k: int = 3) -> List[dict]:
    """
    BM25 关键词检索
    Args:
        query: 用户问题
        top_k: 返回文档数
    Returns:
        文档列表，格式: [{"content": "...", "metadata": {"file_name": "...", "chunk_idx": 0, ...}}, ...]
    """
    body = {
        "query": {
            "match": {
                "content": {
                    "query": query,
                    "operator": "or",  # 多个关键词满足其一即可
                }
            }
        },
        "size": top_k,
    }

    response = es.search(index=INDEX_NAME, body=body)

    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "content": source["content"],
            "metadata": {
                "title": source.get("title", ""),
                "file_name": source.get("file_name", ""),
                "chunk_idx": source.get("chunk_idx", 0),
            }
        })

    return results


if __name__ == "__main__":
    # 简单测试
    query = "上班时间是几点"
    test_query = "公司上班打卡规定"
    print(f"查询: {test_query}")
    results = bm25_search(test_query, top_k=3)
    print(f"命中 {len(results)} 条:")
    for i, doc in enumerate(results):
        print(f"\n{i+1}. {doc['metadata']['file_name']} | chunk_idx={doc['metadata']['chunk_idx']}")
        print(f"   内容: {doc['content'][:]}...")


