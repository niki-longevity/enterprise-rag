# 文档加载
# 使用LangChain加载政策文档（Markdown格式）
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader


def load_policy_documents(data_dir: str = None) -> List[dict]:
    """
    使用LangChain加载政策文档

    Args:
        data_dir: 政策文档目录，None则自动查找

    Returns:
        文档列表，格式: [{"title": "...", "content": "...", "file_path": "..."}]
    """
    if data_dir is None:
        # 使用相对于项目根目录的路径
        current_file = Path(__file__)
        # src/rag/loader.py -> ../../data/policies
        project_root = current_file.parent.parent.parent
        data_dir = project_root / "data" / "policies"

    dir_path = Path(data_dir)
    if not dir_path.exists():
        print(f"警告：政策文档目录不存在: {dir_path}")
        return []

    # 使用LangChain的DirectoryLoader加载所有Markdown文件
    loader = DirectoryLoader(
        path=str(dir_path),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()

    # 转换格式
    docs = []
    for doc in documents:
        file_path = Path(doc.metadata["source"])
        docs.append({
            "title": file_path.stem,
            "content": doc.page_content,
            "file_path": str(file_path)
        })

    return docs
