"""
资源查询端到端测试
测试用例："现在有闲置的投影仪吗"
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.graph import agent_graph
from src.agent.state import AgentState


def test_resource_query():
    """测试资源查询链路"""
    print("=" * 60)
    print("阶段二：资源查询链路测试")
    print("=" * 60)

    # 1. 测试问题
    test_query = "现在有闲置的投影仪吗"
    print(f"\n[步骤1] 测试问题: {test_query}")

    # 2. 构建初始状态
    initial_state: AgentState = {
        "user_id": "test_user_002",
        "session_id": "test_session_002",
        "message": test_query,
        "intent": None,
        "retrieved_docs": [],
        "resources": [],
        "answer": None,
    }

    # 3. 调用LangGraph
    print("\n[步骤2] 调用LangGraph处理...")
    print("  注意：此测试需要Java服务正在运行并提供资源API")
    print("  如果Java服务未运行，将无法获取真实资源数据\n")

    try:
        result = agent_graph.invoke(initial_state)

        # 4. 输出结果
        print("\n[结果]")
        print(f"识别意图: {result.get('intent')}")
        print(f"查询到资源数: {len(result.get('resources', []))}")
        for i, res in enumerate(result.get('resources', [])):
            print(f"  资源{i+1}: {res.get('name')} ({res.get('type')}) - {res.get('status')}")
        print(f"\n最终回答:\n{result.get('answer')}")
    except Exception as e:
        print(f"测试时出现错误: {e}")
        print("\n提示：请确保Java服务正在运行在 http://localhost:8080")
        print("      并已启动资源数据生成器")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_resource_query()
