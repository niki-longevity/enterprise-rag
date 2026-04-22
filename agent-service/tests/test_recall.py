"""
RAG召回测试脚本
对每个query执行检索，对比期望chunk，输出命中率和详细结果
"""
from src.rag.retriever import vector_store
from tests.recall_test_data import test_cases


def run_recall_test(top_k=3):
    """
    执行召回测试
    Args:
        top_k: 每次检索返回的chunk数量
    """
    total = len(test_cases)
    hit_all = 0       # 期望chunk全部命中
    hit_partial = 0   # 至少命中一个期望chunk
    miss = 0          # 完全未命中

    details = []

    for query, expected_chunks in test_cases:
        expected_set = set(expected_chunks)  # {(file_name, chunk_idx), ...}

        # 检索
        results = vector_store.similarity_search(query, top_k)
        actual_set = set()
        for doc in results:
            actual_set.add((doc.metadata["file_name"], doc.metadata["chunk_idx"]))

        # 计算命中
        matched = expected_set & actual_set
        hit_rate = len(matched) / len(expected_set)

        if hit_rate == 1.0:
            hit_all += 1
            status = "ALL_HIT"
        elif hit_rate > 0:
            hit_partial += 1
            status = "PARTIAL"
        else:
            miss += 1
            status = "MISS"

        details.append({
            "query": query,
            "status": status,
            "hit_rate": hit_rate,
            "expected": expected_chunks,
            "matched": sorted(matched),
            "missed": sorted(expected_set - actual_set),
            "actual": [(doc.metadata["file_name"], doc.metadata["chunk_idx"]) for doc in results],
        })

    # 输出汇总
    print("=" * 60)
    print(f"RAG召回测试报告 (top_k={top_k})")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"全部命中: {hit_all} ({hit_all/total:.1%})")
    print(f"部分命中: {hit_partial} ({hit_partial/total:.1%})")
    print(f"完全未命中: {miss} ({miss/total:.1%})")
    print()

    # 输出非全命中的详情
    print("-" * 60)
    print("未全部命中的case:")
    print("-" * 60)
    for d in details:
        if d["status"] != "ALL_HIT":
            print(f"\n[{d['status']}] Q: {d['query']}")
            print(f"  期望: {d['expected']}")
            print(f"  命中: {d['matched']}")
            print(f"  缺失: {d['missed']}")
            print(f"  实际返回: {d['actual']}")

    # 输出全命中概览
    print()
    print("-" * 60)
    print("全部命中的case:")
    print("-" * 60)
    for d in details:
        if d["status"] == "ALL_HIT":
            print(f"  [OK] {d['query']}")

    return details


if __name__ == "__main__":
    run_recall_test(top_k=3)
