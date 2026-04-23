# 测试链路一：政策问答
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.graph import agent_graph


def test_policy_qa_flow():
    """
    测试链路一：政策问答
    从Python Agent服务 -> RAG检索 -> 返回结果
    """
    user_id = "user001"
    message = "婚假能请几天？"
    session_id = "test_session_001"

    system_prompt = "如果需要检索政策，请先对用户的提问进行合适的 Query 改写。"

    initial_state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ],
        "user_id": user_id,
        "session_id": session_id,
    }

    print(f"用户问题: {message}")

    result = agent_graph.invoke(initial_state)
    reply = result["messages"][-1].content

    print(f"助手回复: {reply}")
    print(f"会话ID: {session_id}")


if __name__ == "__main__":
    test_policy_qa_flow()
