# ES初始化入口
# 加载政策文档、分块并存入Elasticsearch
from src.rag.loader import load_policy_documents
from src.rag.splitter import split_document_by_title
from src.es.indexer import create_index, add_documents


def init_es():
    """初始化ES索引并入库"""
    print("正在加载政策文档...")
    docs = load_policy_documents()
    print(f"已加载 {len(docs)} 个文档")

    all_chunks = []
    for doc in docs:
        print(f"正在切分文档: {doc['title']}")
        chunks = split_document_by_title(doc["content"], doc["title"])
        all_chunks.extend(chunks)

    print(f"共切分成 {len(all_chunks)} 个文档块")

    print("正在创建ES索引...")
    create_index()

    print("正在存入ES...")
    add_documents(all_chunks)
    print("ES初始化完成！")


if __name__ == "__main__":
    init_es()
