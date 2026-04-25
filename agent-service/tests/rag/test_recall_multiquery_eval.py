"""
多Query扩展召回测试
向量检索 + ES BM25 多路召回，统一合并去重后精排，计算 Hit Rate 和 MRR
"""
from src.rag.retriever import search_no_rerank
from src.es.searcher import bm25_search
from dashscope.rerank.text_rerank import TextReRank
from src.config.settings import settings as app_settings
from tests.rag.title.recall_test_data import (
    # simple_test_cases,
    complex_test_cases,
    # colloquial_test_cases,
)
# from tests.rag.title.recall_test_data_bm25 import bm25_query_map


# 第一种方案（已废弃，保留注释）
# def multi_retrieve(vec_queries, bm25_query, retrieve_top_k=10, rerank_top_k=5): ...

def multi_retrieve_v2(vec_queries, bm25_query, retrieve_top_k=10, rerank_top_k=2):
    """
    第二种方案：每个query独立检索+用自己的query精排，各取top2，合并去重
    3个向量query + 1个BM25 query = 共约8个结果
    """
    seen = set()
    merged_docs = []

    # 向量检索：3个扩展query，每个独立检索+精排
    for query in vec_queries:
        vec_results = search_no_rerank(query, 5)
        if vec_results:
            # 用该query精排
            doc_texts = [doc["content"] for doc in vec_results]
            response = TextReRank.call(
                model="qwen3-vl-rerank",
                query=query,  # 用自己的query
                documents=doc_texts,
                top_n=5,
                api_key=app_settings.dashscope_api_key,
            )
            for result in response.output.results:
                idx = result.index
                if idx < len(vec_results):
                    doc = vec_results[idx]
                    key = (doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"])
                    if key not in seen:
                        seen.add(key)
                        merged_docs.append(doc)

    # # BM25检索：1个query，独立检索+精排
    # es_results = bm25_search(bm25_query, 10)
    # if es_results:
    #     doc_texts = [doc["content"] for doc in es_results]
    #     response = TextReRank.call(
    #         model="qwen3-vl-rerank",
    #         query=vec_queries[0],  # 用意图提纯后的 query
    #         documents=doc_texts,
    #         top_n=5,
    #         api_key=app_settings.dashscope_api_key,
    #     )
    #     for result in response.output.results:
    #         idx = result.index
    #         if idx < len(es_results):
    #             doc = es_results[idx]
    #             key = (doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"])
    #             if key not in seen:
    #                 seen.add(key)
    #                 merged_docs.append(doc)

    return merged_docs


def rerank_merged(original_query, merged_docs, top_k=5):
    """
    对合并后的文档用原始query精排，返回 top_k 的 (file_name, chunk_idx) 列表
    """
    if not merged_docs:
        return []

    doc_texts = [doc["content"] for doc in merged_docs]
    response = TextReRank.call(
        model="qwen3-vl-rerank",
        query=original_query,
        documents=doc_texts,
        top_n=top_k,
        api_key=app_settings.dashscope_api_key,
    )
    reranked = []
    for result in response.output.results:
        idx = result.index
        if idx < len(merged_docs):
            doc = merged_docs[idx]
            reranked.append((doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"]))
    return reranked[:top_k]


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


def run_recall_eval(test_cases, retrieve_top_k=10, rerank_top_k=2):
    """第二种方案：每个query独立检索+精排，各取top2，共约8个结果"""
    total = len(test_cases)
    hit_all = 0
    hit_partial = 0
    miss = 0
    hit_rates = []
    mrrs = []

    for original_query, expanded_queries, expected_chunks in test_cases:
        expected_set = set(expected_chunks)
        # bm25_query = bm25_query_map.get(original_query, original_query)
        bm25_query = original_query

        # 第二种方案：每个query独立检索+精排，合并去重
        merged_docs = multi_retrieve_v2(expanded_queries, bm25_query, retrieve_top_k, rerank_top_k)

        # 已经是精排后的结果，直接转换
        actual_chunks = [
            (doc["metadata"]["file_name"], doc["metadata"]["chunk_idx"])
            for doc in merged_docs
        ]

        print(f"精排合并去重后，剩下文档数: {len(actual_chunks)}")

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

    print(f"  [第二种方案：每个query独立检索+精排，各取top{rerank_top_k}]")
    print(f"  测试数: {total}")
    print(f"  全部命中: {hit_all} ({hit_all / total:.1%})")
    print(f"  部分命中: {hit_partial} ({hit_partial / total:.1%})")
    print(f"  完全未命中: {miss} ({miss / total:.1%})")
    print(f"  平均 Hit Rate: {sum(hit_rates) / total:.3f}")
    print(f"  MRR: {sum(mrrs) / total:.3f}")


if __name__ == "__main__":
    print("=" * 50)
    print("RAG 多Query扩展 + 多路召回测试（第二种方案）")
    print("=" * 50)

    for name, cases in [
        # ("简单问题", simple_test_cases),
        ("复杂问题", complex_test_cases),
        # ("口语化问题", colloquial_test_cases),
    ]:
        total_q = sum(len(queries) for _, queries, _ in cases)
        print(f"\n--- {name} ({len(cases)} 用例, {total_q} 条扩展query) ---")

        # 第二种方案：每个query独立检索+精排，各取top2，共约8个
        run_recall_eval(cases, retrieve_top_k=10, rerank_top_k=3)
