"""RAG 回答幻觉评估：Faithfulness / Answer Relevancy
从 Agent 图状态中提取实际检索上下文做评估，自定义评分 prompt"""
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from test_data import simple_test_cases, complex_test_cases, colloquial_test_cases
from src.config.settings import settings
from src.agent.graph import agent_graph

# ── 评估 LLM ──────────────────────────────────────────
_eval = ChatOpenAI(
    model=settings.tencent_model,
    api_key=settings.tencent_api_key,
    base_url=settings.tencent_base_url,
    temperature=0.0,
)

FAITHFULNESS_PROMPT = """你是一个 RAG 系统的忠实度评估者。请逐句检查 Agent 回答中的每个陈述，判断它们是否在**上下文（Agent 检索到的文档内容）**中有依据。

## 上下文（Agent 实际检索到的文档）
{context}

## 用户问题
{query}

## Agent 回答
{answer}

## 评分标准
- 5分：完全基于上下文，每个陈述都能找到明确依据，无任何编造
- 4分：绝大部分陈述有上下文支持，只有极少量合理的语言衔接
- 3分：回答大体基于上下文，但包含一些上下文未明确提及的推断或补充
- 2分：回答中较多信息不在上下文里，明显依赖外部知识
- 1分：回答基本是编造的，与上下文几乎无关

## 输出格式（严格遵守）
请用JSON格式回答：
{{"score": <1-5的整数>, "reason": "<逐条列出哪些陈述有/没有上下文支持，具体引用上下文中的内容>"}}"""

RELEVANCY_PROMPT = """你是一个 RAG 系统的相关性评估者。请判断 Agent 的回答是否直接、完整地回应了用户的问题。

## 用户问题
{query}

## Agent 回答
{answer}

## 评分标准
- 5分：精准切题，完整回应了问题的所有要点
- 4分：基本切题，遗漏了少量要点或包含少量无关内容
- 3分：部分相关，遗漏了重要要点，或包含较多无关内容
- 2分：勉强相关，大量内容与问题无关
- 1分：完全不相关，答非所问

## 输出格式（严格遵守）
请用JSON格式回答：
{{"score": <1-5的整数>, "reason": "<具体说明回答覆盖了问题的哪些要点、遗漏了什么、哪些内容无关>"}}"""


def get_agent_result(query: str) -> Tuple[str, str]:
    """用 Agent 图生成回答，同时提取 Agent 实际检索到的上下文"""
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "user_id": "eval",
        "session_id": "eval_session",
    }
    result = agent_graph.invoke(initial_state, config={"recursion_limit": 20})

    # 提取所有 ToolMessage 内容作为评估上下文
    context_parts = []
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage) and msg.content:
            context_parts.append(msg.content)
    context = "\n\n---\n\n".join(context_parts) if context_parts else "（Agent 未调用检索工具）"

    # 提取最终 AI 回答
    answer = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            answer = msg.content
            break

    return answer or "（无回答）", context


def evaluate_with_prompt(prompt_template: str, query: str, answer: str,
                         context: str = None) -> Tuple[int, str]:
    """用自定义 prompt 调用评估 LLM，返回 (score, reason)"""
    if context:
        prompt = prompt_template.format(query=query, answer=answer, context=context)
    else:
        prompt = prompt_template.format(query=query, answer=answer)

    response = _eval.invoke(prompt)
    raw = response.content.strip()

    # 提取 JSON
    import json
    try:
        # 去除可能的 markdown 代码块标记
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3]
        data = json.loads(raw)
        return int(data["score"]), data["reason"]
    except (json.JSONDecodeError, KeyError, ValueError):
        # 解析失败时尝试从文本中提取分数
        return 0, raw[:200]


def evaluate_one(query: str) -> dict:
    """评估单个测试用例"""
    # 1. Agent 生成回答 + 提取真实检索上下文
    answer, context = get_agent_result(query)

    # 2. Faithfulness：回答是否忠于 Agent 实际检索到的上下文
    faith_score, faith_reason = evaluate_with_prompt(
        FAITHFULNESS_PROMPT, query, answer, context=context
    )

    # 3. Answer Relevancy：回答是否切题
    relev_score, relev_reason = evaluate_with_prompt(
        RELEVANCY_PROMPT, query, answer
    )

    return {
        "query": query,
        "answer": answer,
        "context": context,
        "faithful_score": faith_score,
        "faithful_reason": faith_reason,
        "relevant_score": relev_score,
        "relevant_reason": relev_reason,
    }


def evaluate_category(cases: List[Tuple[str, list]], name: str,
                      report_path: str = None):
    """评估一组测试用例并汇总"""
    print(f"\n{'='*60}")
    print(f"  {name} ({len(cases)} cases)")
    print(f"{'='*60}")

    results = []
    faith_sum = relev_sum = 0.0
    report_lines = [] if report_path else None

    for i, (query, _expected) in enumerate(cases, 1):
        print(f"\n[{i:2d}] 评估中: {query}")
        r = evaluate_one(query)
        results.append(r)

        faith_sum += r["faithful_score"]
        relev_sum += r["relevant_score"]

        print(f"    Faith={r['faithful_score']}/5, Relev={r['relevant_score']}/5")
        print(f"    Faith理由: {r['faithful_reason'][:150]}")
        print(f"    Relev理由: {r['relevant_reason'][:150]}")

        if report_lines is not None:
            report_lines.append(f"## [{i}] {query}\n")
            report_lines.append(f"\n### Agent 回答\n\n{r['answer']}\n")
            report_lines.append(f"\n### Agent 检索上下文\n\n{r['context'][:3000]}\n")
            report_lines.append(f"\n### Faithfulness: **{r['faithful_score']}/5**\n")
            report_lines.append(f"> {r['faithful_reason']}\n")
            report_lines.append(f"\n### Answer Relevancy: **{r['relevant_score']}/5**\n")
            report_lines.append(f"> {r['relevant_reason']}\n")
            report_lines.append(f"\n---\n")

    n = len(cases)
    print(f"\n  {name} 汇总")
    print(f"  Faithfulness:     avg={faith_sum/n:.1f}/5")
    print(f"  Answer Relevancy: avg={relev_sum/n:.1f}/5")

    if report_lines is not None:
        summary = (
            f"# {name} 评估报告\n\n"
            f"| 指标 | 平均分 |\n|------|--------|\n"
            f"| Faithfulness | {faith_sum/n:.1f}/5 |\n"
            f"| Answer Relevancy | {relev_sum/n:.1f}/5 |\n"
        )
        report_lines.insert(0, summary)
        Path(report_path).write_text("\n".join(report_lines), encoding="utf-8")
        print(f"\n  详细报告已保存: {report_path}")

    return {"faithfulness": faith_sum / n,
            "relevancy": relev_sum / n}


def evaluate_one_to_file(args: Tuple[int, str]) -> Tuple[int, int, int]:
    """评估单个用例并写入独立 .md 文件，返回 (idx, faith_score, relev_score)"""
    idx, query = args
    r = evaluate_one(query)

    md = (
        f"# [{idx}] {query}\n\n"
        f"## Agent 回答\n\n{r['answer']}\n\n"
        f"## Agent 检索上下文\n\n{r['context'][:3000]}\n\n"
        f"## Faithfulness: **{r['faithful_score']}/5**\n\n> {r['faithful_reason']}\n\n"
        f"## Answer Relevancy: **{r['relevant_score']}/5**\n\n> {r['relevant_reason']}\n"
    )
    out_path = f"eval_case_{idx:02d}.md"
    Path(out_path).write_text(md, encoding="utf-8")
    print(f"  [{idx:2d}] 完成 → {out_path}  Faith={r['faithful_score']}/5  Relev={r['relevant_score']}/5")
    return idx, r["faithful_score"], r["relevant_score"]


def evaluate_category_parallel(cases: List[Tuple[str, list]], name: str,
                               workers: int = 5, start_idx: int = 1):
    """并行评估一组测试用例，每个用例输出独立的 .md"""
    from concurrent.futures import ThreadPoolExecutor
    queries = [(i, query) for i, (query, _expected) in enumerate(cases, start_idx)]

    print(f"{'='*60}")
    print(f"  {name} ({len(cases)} cases, {workers} parallel)")
    print(f"{'='*60}")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(evaluate_one_to_file, queries))

    faith_sum = sum(r[1] for r in results)
    relev_sum = sum(r[2] for r in results)
    n = len(cases)

    print(f"\n  Faith={faith_sum/n:.1f}/5  Relev={relev_sum/n:.1f}/5  ({n} cases)")


if __name__ == "__main__":
    evaluate_category_parallel(complex_test_cases[25:45], "Complex",
                               workers=20, start_idx=26)
