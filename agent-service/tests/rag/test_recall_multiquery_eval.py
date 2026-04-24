"""
多Query扩展召回测试
对每个用例的多个扩展 query 分别检索，合并去重后计算 Hit Rate 和 MRR
"""
from src.rag.retriever import search
from tests.rag.fixed_overlap.recall_test_data_multiquery import (
    simple_test_cases,
    complex_test_cases,
    colloquial_test_cases,
)


def multi_query_search(expanded_queries, top_k):
    """对多个扩展查询分别检索，合并去重，按首次出现顺序排列"""
    seen = set()
    merged = []
    for query in expanded_queries:
        results = search(query, top_k)
        for doc in results:
            key = (doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"])
            if key not in seen:
                seen.add(key)
                merged.append(key)
    return merged


def calculate_mrr(expected_chunks, actual_chunks):
    best_rank = float("inf")
    for expected in expected_chunks:
        try:
            rank = actual_chunks.index(expected) + 1
            if rank < best_rank:
                best_rank = rank
        except ValueError:
            continue
    return 1.0 / best_rank if best_rank != float("inf") else 0.0


def run_recall_eval(test_cases, top_k=15):
    total = len(test_cases)
    hit_all = 0
    hit_partial = 0
    miss = 0
    hit_rates = []
    mrrs = []

    for original_query, expanded_queries, expected_chunks in test_cases:
        expected_set = set(expected_chunks)

        actual_chunks = multi_query_search(expanded_queries, top_k)
        matched = expected_set & set(actual_chunks)
        hit_rate = len(matched) / len(expected_set)

        hit_rates.append(hit_rate)
        mrrs.append(calculate_mrr(expected_chunks, actual_chunks))

        if hit_rate == 1.0:
            hit_all += 1
        elif hit_rate > 0:
            hit_partial += 1
        else:
            miss += 1

    print(f"  测试数: {total}")
    print(f"  全部命中: {hit_all} ({hit_all / total:.1%})")
    print(f"  部分命中: {hit_partial} ({hit_partial / total:.1%})")
    print(f"  完全未命中: {miss} ({miss / total:.1%})")
    print(f"  平均 Hit Rate: {sum(hit_rates) / total:.3f}")
    print(f"  MRR: {sum(mrrs) / total:.3f}")


if __name__ == "__main__":
    print("=" * 50)
    print("RAG 多Query扩展召回测试")
    print("=" * 50)

    for name, cases in [
        ("简单问题", simple_test_cases),
        ("复杂问题", complex_test_cases),
        ("口语化问题", colloquial_test_cases),
    ]:
        total_q = sum(len(queries) for _, queries, _ in cases)
        print(f"\n--- {name} ({len(cases)} 用例, {total_q} 条扩展query) ---")
        run_recall_eval(cases)
