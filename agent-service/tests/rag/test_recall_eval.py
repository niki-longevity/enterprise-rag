"""使用 LlamaIndex RetrieverEvaluator 进行 RAG 召回指标测试"""
from llama_index.core.evaluation import RetrieverEvaluator
from llama_index.core import QueryBundle
from src.rag.retriever import index
from tests.rag.fixed_overlap.recall_test_data import (
    simple_test_cases,
    complex_test_cases,
    colloquial_test_cases,
)


def run_recall_eval(test_cases, top_k=5):
    """用 RetrieverEvaluator 跑一批测试用例，返回 Hit Rate 和 MRR"""
    retriever = index.as_retriever(similarity_top_k=top_k)
    evaluator = RetrieverEvaluator()

    query_bundles = []
    expected_ids_list = []

    for query, expected_chunks in test_cases:
        qb = QueryBundle(query_str=query)
        expected_ids = [
            f"{file_name}::{chunk_idx}" for file_name, chunk_idx in expected_chunks
        ]
        query_bundles.append(qb)
        expected_ids_list.append(expected_ids)

    results = evaluator.evaluate_dataset(
        query_bundles=query_bundles,
        expected_ids_list=expected_ids_list,
        retriever=retriever,
    )

    # 汇总指标
    hit_rates = [r.hit_rate for r in results]
    mrrs = [r.mrr for r in results]
    total = len(results)
    hit_all = sum(1 for h in hit_rates if h == 1.0)
    hit_any = sum(1 for h in hit_rates if h > 0)
    miss = sum(1 for h in hit_rates if h == 0)

    print(f"  测试数: {total}")
    print(f"  全部命中: {hit_all} ({hit_all / total:.1%})")
    print(f"  部分命中: {hit_any - hit_all} ({(hit_any - hit_all) / total:.1%})")
    print(f"  完全未命中: {miss} ({miss / total:.1%})")
    print(f"  平均 Hit Rate: {sum(hit_rates) / total:.3f}")
    print(f"  MRR: {sum(mrrs) / total:.3f}")

    return results


if __name__ == "__main__":
    print("=" * 50)
    print("RAG 召回测试 (LlamaIndex RetrieverEvaluator)")
    print("=" * 50)

    for name, cases in [
        ("简单问题", simple_test_cases),
        ("复杂问题", complex_test_cases),
        ("口语化问题", colloquial_test_cases),
    ]:
        print(f"\n--- {name} ({len(cases)} 条) ---")
        run_recall_eval(cases)
