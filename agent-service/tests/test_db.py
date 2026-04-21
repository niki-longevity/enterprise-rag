# 测试数据库操作
from src.db.session import SessionLocal
from src.db.models import ChatHistory
from src.db.mapper import ChatHistoryMapper
import src.db


def test_db_operations():
    """测试数据库CRUD操作"""
    db = SessionLocal()
    mapper = ChatHistoryMapper(db)

    test_session_id = "test_session_123"
    test_user_id = "test_user_001"

    print("=== 测试1: 保存用户消息 ===")
    user_msg = ChatHistory(
        session_id=test_session_id,
        user_id=test_user_id,
        role="USER",
        content="婚假能请几天？"
    )
    saved_user = mapper.save(user_msg)
    print(f"保存成功: id={saved_user.id}, content={saved_user.content}")

    print("\n=== 测试2: 保存助手回复 ===")
    assistant_msg = ChatHistory(
        session_id=test_session_id,
        user_id=test_user_id,
        role="ASSISTANT",
        content="根据《休假管理规定》，婚假可以请3天。"
    )
    saved_assistant = mapper.save(assistant_msg)
    print(f"保存成功: id={saved_assistant.id}, content={saved_assistant.content}")

    print("\n=== 测试3: 根据会话ID查询历史 ===")
    history = mapper.list_by_session_id(test_session_id)
    print(f"查询到 {len(history)} 条消息:")
    for msg in history:
        print(f"  [{msg.role}] {msg.content}")

    print("\n=== 测试4: 根据ID查询 ===")
    found = mapper.get_by_id(saved_user.id)
    if found:
        print(f"查询到: id={found.id}, content={found.content}")

    print("\n=== 测试5: 获取用户的会话列表 ===")
    sessions = mapper.list_session_ids_by_user_id(test_user_id)
    print(f"用户 {test_user_id} 的会话: {sessions}")

    db.close()
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_db_operations()
