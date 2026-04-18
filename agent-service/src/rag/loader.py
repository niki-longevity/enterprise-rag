# 文档加载
# 加载政策文档（Markdown格式）
from pathlib import Path
from typing import List


def load_policy_documents(data_dir: str = "./data/policies") -> List[dict]:
    # 从data/policies目录加载所有Markdown政策文档
    docs = []
    dir_path = Path(data_dir)
    if not dir_path.exists():
        return docs
    for file_path in dir_path.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        docs.append({
            "title": file_path.stem,
            "content": content,
            "file_path": str(file_path)
        })
    return docs
