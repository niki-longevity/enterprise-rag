# ES索引管理
# 将政策文档chunk存入Elasticsearch，支持全文检索
from elasticsearch import Elasticsearch
from src.config.settings import settings

INDEX_NAME = "policies"

# 中文全文检索的mapping
INDEX_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "ik_smart_analyzer": {
                    "type": "custom",
                    "tokenizer": "ik_smart"
                },
                "ik_max_word_analyzer": {
                    "type": "custom",
                    "tokenizer": "ik_max_word"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "file_name": {
                "type": "keyword"
            },
            "chunk_idx": {
                "type": "integer"
            },
            "title": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
}


def get_es_client() -> Elasticsearch:
    """获取ES客户端"""
    return Elasticsearch(f"http://{settings.es_host}:{settings.es_port}")


def create_index(es: Elasticsearch = None):
    """
    创建索引，如果已存在则先删除
    如果ES没安装IK分词器，回退到标准分词
    """
    if es is None:
        es = get_es_client()

    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)

    try:
        es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
        print(f"索引 {INDEX_NAME} 创建成功（IK分词器）")
    except Exception as e:
        if "ik_max_word" in str(e) or "analyzer" in str(e).lower():
            # IK分词器不可用，使用标准分词回退
            fallback_mapping = {
                "mappings": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            }
                        },
                        "file_name": {"type": "keyword"},
                        "chunk_idx": {"type": "integer"},
                        "title": {
                            "type": "text",
                            "fields": {"keyword": {"type": "keyword"}}
                        }
                    }
                }
            }
            if es.indices.exists(index=INDEX_NAME):
                es.indices.delete(index=INDEX_NAME)
            es.indices.create(index=INDEX_NAME, body=fallback_mapping)
            print(f"索引 {INDEX_NAME} 创建成功（标准分词，建议安装IK分词插件以提升中文检索效果）")
        else:
            raise


def add_documents(chunks: list, es: Elasticsearch = None):
    """
    将chunk批量存入ES
    Args:
        chunks: 文档块列表，格式同rag/splitter输出 [{"title", "content", "file_name", "chunk_idx"}, ...]
        es: ES客户端，None则自动创建
    """
    if es is None:
        es = get_es_client()

    actions = []
    for chunk in chunks:
        doc_id = f"{chunk['file_name']}::{chunk['chunk_idx']}"
        actions.append({
            "_index": INDEX_NAME,
            "_id": doc_id,
            "_source": {
                "content": chunk["content"],
                "file_name": chunk["file_name"],
                "chunk_idx": chunk["chunk_idx"],
                "title": chunk["title"],
            }
        })

    from elasticsearch.helpers import bulk
    success, failed = bulk(es, actions, raise_on_error=False)
    print(f"ES入库完成: 成功 {success}, 失败 {len(failed)}")
    return success, len(failed)


def clear(es: Elasticsearch = None):
    """清空ES索引"""
    if es is None:
        es = get_es_client()

    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"索引 {INDEX_NAME} 已删除")
