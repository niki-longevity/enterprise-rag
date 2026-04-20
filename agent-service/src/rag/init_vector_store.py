"""
初始化向量库
加载政策文档、分块并存入ChromaDB
"""
from src.rag.loader import load_policy_documents
from src.rag.splitter import split_document_by_title
from src.rag.retriever import get_policy_retriever


def init_vector_store():
    """初始化向量库"""
    print("正在加载政策文档...")
    docs = load_policy_documents()
    print(f"已加载 {len(docs)} 个文档")

    all_chunks = []
    for doc in docs:
        print(f"正在切分文档: {doc['title']}")
        chunks = split_document_by_title(doc["content"], doc["title"])
        all_chunks.extend(chunks)

    print(f"共切分成 {len(all_chunks)} 个文档块")

    print("正在存入向量库...")
    retriever = get_policy_retriever()
    retriever.clear()
    retriever.add_documents(all_chunks)

    print("向量库初始化完成！")
    return retriever


if __name__ == "__main__":
    init_vector_store()
