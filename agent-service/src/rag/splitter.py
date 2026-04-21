# 文档分块
# 使用LangChain把政策文档切分成小块，用于向量检索
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_document_by_title(content: str, title: str) -> List[dict]:
    """
    使用LangChain的RecursiveCharacterTextSplitter切分文档

    Args:
        content: 文档内容
        title: 文档标题

    Returns:
        文档块列表，格式: [{"title": "...", "content": "..."}]
    """
    # 使用LangChain的RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    # 切分文档
    chunks = splitter.split_text(content)

    # 转换格式
    result = []
    for i, chunk_content in enumerate(chunks):
        result.append({
            "title": f"{title} - 第{i+1}段",
            "content": chunk_content
        })

    return result
