"""临时脚本：输出向量库中所有chunk的元数据和完整内容到md文件"""
from src.rag.retriever import get_all_chunks

chunks = get_all_chunks()
output_path = "title/按二级标题.md"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"# 向量库全量Chunk ({len(chunks)}个)\n\n")
    for i, doc in enumerate(chunks):
        meta = doc["metadata"]
        f.write(f"## [{i}] {meta['file_name']} | chunk_idx={meta['chunk_idx']}\n\n")
        f.write(f"{doc['content']}\n\n---\n\n")

print(f"已输出到 {output_path}，共 {len(chunks)} 个chunk")
