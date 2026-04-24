# 文档分块
# 使用LlamaIndex把政策文档切分成小块，用于向量检索
import re
from typing import List
from llama_index.core.node_parser import SentenceSplitter


def clean_text(text: str) -> str:
    """
    清理文本格式，优化向量检索质量
    - 合并连续换行
    - 去除行首尾空格
    - 保留段落结构
    """
    # 替换 \r\n 为 \n
    text = text.replace("\r\n", "\n")

    # 合并 3 个以上连续换行为 2 个
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 去除每行首尾空格
    lines = [line.strip() for line in text.split("\n")]

    # 重新拼接，过滤空行（但保留段落分隔）
    cleaned_lines = []
    for line in lines:
        if line:
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != "":  # 避免连续空行
            cleaned_lines.append("")

    return "\n".join(cleaned_lines)


def split_document_by_title(content: str, title: str) -> List[dict]:
    """
    使用LlamaIndex的SentenceSplitter切分文档
    Args:
        content: 文档内容
        title: 文档标题
    Returns:
        文档块列表，格式: [{"title": "...", "content": "...", "file_name": "...", "chunk_idx": i}]
    """
    # 先清理文本
    content = clean_text(content)

    splitter = SentenceSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(content)

    result = []
    for i, chunk_content in enumerate(chunks):
        result.append({
            "title": f"{title} - 第{i+1}段",
            "content": chunk_content,
            "file_name": title,
            "chunk_idx": i
        })

    return result
