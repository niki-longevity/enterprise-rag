# 文档分块
# 把政策文档切分成小块，用于向量检索
from typing import List


def split_document_by_title(content: str, title: str) -> List[dict]:
    # 按Markdown标题切分文档（# 或 ##）
    chunks = []
    lines = content.split("\n")
    current_chunk = []
    current_title = title

    for line in lines:
        if line.startswith("# "):
            # 遇到一级标题，保存上一个chunk
            if current_chunk:
                chunks.append({
                    "title": current_title,
                    "content": "\n".join(current_chunk).strip()
                })
            current_title = line[2:].strip()
            current_chunk = [line]
        elif line.startswith("## "):
            # 遇到二级标题，也保存上一个chunk
            if current_chunk:
                chunks.append({
                    "title": current_title,
                    "content": "\n".join(current_chunk).strip()
                })
            current_title = f"{title} - {line[3:].strip()}"
            current_chunk = [line]
        else:
            current_chunk.append(line)

    # 保存最后一个chunk
    if current_chunk:
        chunks.append({
            "title": current_title,
            "content": "\n".join(current_chunk).strip()
        })

    return chunks
