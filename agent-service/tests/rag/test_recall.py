"""
RAG召回测试脚本
对每个query执行检索，对比期望chunk，输出命中率和详细结果
支持三种测试类型分别测试：简单问题、复杂问题、口语化问题
"""
from src.rag.retriever import vector_store
from tests.rag.fixed_overlap.recall_test_data import simple_test_cases, complex_test_cases, colloquial_test_cases, test_cases


def run_recall_test_for_category(test_cases, category_name, top_k=3):
    """
    执行指定类别的召回测试

    Args:
        test_cases: 测试用例列表
        category_name: 类别名称
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
        hit_rate = len(matched) / len(expected_set) if expected_set else 0

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
    print(f"RAG召回测试报告 - {category_name} (top_k={top_k})")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"全部命中: {hit_all} ({hit_all/total:.1%})")
    print(f"部分命中: {hit_partial} ({hit_partial/total:.1%})")
    print(f"完全未命中: {miss} ({miss/total:.1%})")

    # 输出平均期望chunk数
    avg_expected = sum(len(case[1]) for case in test_cases) / total
    print(f"平均期望chunk数: {avg_expected:.1f}")
    print()

    # 输出非全命中的详情
    print("-" * 60)
    print(f"未全部命中的case ({category_name}):")
    print("-" * 60)
    for d in details:
        if d["status"] != "ALL_HIT":
            print(f"\n[{d['status']}] Q: {d['query']}")
            print(f"  期望: {d['expected']}")
            print(f"  命中: {d['matched']}")
            print(f"  缺失: {d['missed']}")
            print(f"  实际返回: {d['actual']}")

    return details


def run_recall_test(top_k=3):
    """
    执行召回测试（保持向后兼容）
    Args:
        top_k: 每次检索返回的chunk数量
    """
    # 使用test_cases保持向后兼容
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


def run_comprehensive_recall_test(top_k=3):
    """
    执行全面的召回测试，包括所有三类问题
    """
    print("=" * 60)
    print("RAG系统综合召回测试报告")
    print("=" * 60)
    print()

    # 分别测试三类问题
    simple_details = run_recall_test_for_category(simple_test_cases, "简单问题", top_k)
    print("\n" + "=" * 60)
    complex_details = run_recall_test_for_category(complex_test_cases, "复杂问题", top_k)
    print("\n" + "=" * 60)
    colloquial_details = run_recall_test_for_category(colloquial_test_cases, "口语化问题", top_k)

    # 汇总统计
    print("\n" + "=" * 60)
    print("综合统计汇总")
    print("=" * 60)

    categories = [
        ("简单问题", simple_test_cases, simple_details),
        ("复杂问题", complex_test_cases, complex_details),
        ("口语化问题", colloquial_test_cases, colloquial_details),
    ]

    all_cases = []
    all_details = []

    for name, cases, details in categories:
        total = len(cases)
        hit_all = sum(1 for d in details if d["status"] == "ALL_HIT")
        hit_partial = sum(1 for d in details if d["status"] == "PARTIAL")
        miss = sum(1 for d in details if d["status"] == "MISS")

        print(f"\n{name}:")
        print(f"  测试数: {total}")
        print(f"  全部命中率: {hit_all/total:.1%} ({hit_all}/{total})")
        print(f"  部分命中率: {hit_partial/total:.1%} ({hit_partial}/{total})")
        print(f"  未命中率: {miss/total:.1%} ({miss}/{total})")

        all_cases.extend(cases)
        all_details.extend(details)

    # 总体统计
    total_all = len(all_cases)
    hit_all_all = sum(1 for d in all_details if d["status"] == "ALL_HIT")
    hit_partial_all = sum(1 for d in all_details if d["status"] == "PARTIAL")
    miss_all = sum(1 for d in all_details if d["status"] == "MISS")

    print("\n总体统计:")
    print(f"  总测试数: {total_all}")
    print(f"  总体全部命中率: {hit_all_all/total_all:.1%} ({hit_all_all}/{total_all})")
    print(f"  总体部分命中率: {hit_partial_all/total_all:.1%} ({hit_partial_all}/{total_all})")
    print(f"  总体未命中率: {miss_all/total_all:.1%} ({miss_all}/{total_all})")

    # 分析复杂问题的跨文档检索效果
    print("\n" + "=" * 60)
    print("复杂问题跨文档检索分析")
    print("=" * 60)

    complex_docs_analysis = {}
    for i, (query, expected) in enumerate(complex_test_cases):
        # 统计期望涉及的文档种类
        docs = set(file_name for file_name, _ in expected)
        for doc in docs:
            complex_docs_analysis[doc] = complex_docs_analysis.get(doc, 0) + 1

    print("复杂问题涉及的文档分布:")
    for doc, count in sorted(complex_docs_analysis.items(), key=lambda x: x[1], reverse=True):
        print(f"  {doc}: {count}个问题 ({count/len(complex_test_cases):.1%})")

    # 分析复杂问题的chunk数分布
    chunk_counts = [len(expected) for _, expected in complex_test_cases]
    avg_chunks = sum(chunk_counts) / len(chunk_counts)
    max_chunks = max(chunk_counts)
    min_chunks = min(chunk_counts)

    print(f"\n复杂问题期望chunk数分析:")
    print(f"  平均期望chunk数: {avg_chunks:.1f}")
    print(f"  最多期望chunk数: {max_chunks}")
    print(f"  最少期望chunk数: {min_chunks}")

    return {
        "simple": simple_details,
        "complex": complex_details,
        "colloquial": colloquial_details,
        "all": all_details,
    }


if __name__ == "__main__":
    # 默认运行综合测试
    run_comprehensive_recall_test(top_k=3)