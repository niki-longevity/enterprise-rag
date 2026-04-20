"""
政策问答端到端测试
测试用例："我能不能带宠物上班"
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.init_vector_store import init_vector_store
from src.agent.graph import agent_graph
from src.agent.state import AgentState


def test_policy_qa():
    """测试政策问答链路"""
    print("=" * 60)
    print("阶段二：政策问答链路测试")
    print("=" * 60)

    # 1. 初始化向量库
    print("\n[步骤1] 初始化向量库...")
    init_vector_store()

    # 2. 测试问题
    test_query = "我能不能带宠物上班"
    print(f"\n[步骤2] 测试问题: {test_query}")

    # 3. 构建初始状态
    initial_state: AgentState = {
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "message": test_query,
        "intent": None,
        "retrieved_docs": [],
        "answer": None,
    }

    # 4. 调用LangGraph
    print("\n[步骤3] 调用LangGraph处理...")
    result = agent_graph.invoke(initial_state)

    # 5. 输出结果
    print("\n[结果]")
    print(f"识别意图: {result.get('intent')}")
    print(f"检索到文档数: {len(result.get('retrieved_docs', []))}")
    for i, doc in enumerate(result.get('retrieved_docs', [])):
        print(f"  文档{i+1}: {doc['title']}")
    print(f"\n最终回答:\n{result.get('answer')}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_policy_qa()
