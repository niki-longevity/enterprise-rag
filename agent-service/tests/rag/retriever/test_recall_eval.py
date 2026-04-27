"""
LlamaIndex 召回指标测试
指标计算逻辑与原 test_recall.py 完全一致：命中率 = 命中chunk数/期望chunk数
"""
from src.rag.retriever import search_no_rerank
from tests.rag.retriever.title.recall_test_data_complex import (
    # simple_test_cases,
    complex_test_cases,
    # colloquial_test_cases,
)


def calculate_mrr(expected_chunks, actual_chunks):
    """MRR：最早出现的期望 chunk 排名的倒数"""
    best_rank = float("inf")
    for expected in expected_chunks:
        try:
            rank = actual_chunks.index(expected) + 1
            if rank < best_rank:
                best_rank = rank
        except ValueError:
            continue
    return 1.0 / best_rank if best_rank != float("inf") else 0.0


def run_recall_eval(test_cases, top_k=5):
    total = len(test_cases)
    hit_all = 0
    hit_partial = 0
    miss = 0
    hit_rates = []
    mrrs = []

    for query, expected_chunks in test_cases:
        expected_set = set(expected_chunks)

        results = search_no_rerank(query, top_k)
        actual_chunks = [
            (doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"])
            for doc in results
        ]

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
    print("RAG 召回测试 (LlamaIndex + 原版指标逻辑)")
    print("=" * 50)

    for name, cases in [
        # ("简单问题", simple_test_cases),
        ("复杂问题", complex_test_cases),
        # ("口语化问题", colloquial_test_cases),
    ]:
        print(f"\n--- {name} ({len(cases)} 条) ---")
        run_recall_eval(cases)
