# ES全文检索
# 使用Elasticsearch进行政策文档的全文检索
from typing import List
from elasticsearch import Elasticsearch
from src.config.settings import settings
from src.es.indexer import get_es_client, INDEX_NAME


def search(query: str, top_k: int = 3) -> List[dict]:
    """
    全文检索政策文档
    Args:
        query: 查询文本
        top_k: 返回文档数
    Returns:
        文档列表，格式: [{"content": "...", "file_name": "...", "chunk_idx": 0, "title": "...", "score": 1.0}, ...]
    """
    es = get_es_client()

    result = es.search(
        index=INDEX_NAME,
        body={
            "size": top_k,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content^2", "title"],
                    "type": "best_fields"
                }
            }
        }
    )

    hits = result["hits"]["hits"]
    return [
        {
            "content": hit["_source"]["content"],
            "file_name": hit["_source"]["file_name"],
            "chunk_idx": hit["_source"]["chunk_idx"],
            "title": hit["_source"]["title"],
            "score": hit["_score"],
        }
        for hit in hits
    ]


def search_with_filter(query: str, file_name: str = None, top_k: int = 3) -> List[dict]:
    """
    带过滤条件的全文检索，可按文档名过滤
    Args:
        query: 查询文本
        file_name: 文档名过滤（精确匹配）
        top_k: 返回文档数
    Returns:
        文档列表
    """
    es = get_es_client()

    must = [
        {
            "multi_match": {
                "query": query,
                "fields": ["content^2", "title"],
                "type": "best_fields"
            }
        }
    ]

    filter_clauses = []
    if file_name:
        filter_clauses.append({"term": {"file_name": file_name}})

    body = {
        "size": top_k,
        "query": {
            "bool": {
                "must": must,
                "filter": filter_clauses
            }
        }
    }

    result = es.search(index=INDEX_NAME, body=body)

    hits = result["hits"]["hits"]
    return [
        {
            "content": hit["_source"]["content"],
            "file_name": hit["_source"]["file_name"],
            "chunk_idx": hit["_source"]["chunk_idx"],
            "title": hit["_source"]["title"],
            "score": hit["_score"],
        }
        for hit in hits
    ]
