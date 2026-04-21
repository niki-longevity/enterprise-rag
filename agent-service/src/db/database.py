# 数据库操作
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def get_db_path() -> Path:
    """获取数据库文件路径"""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    db_dir = project_root / "data" / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "chat_history.db"


def init_db():
    """初始化数据库表"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history(session_id)
    """)

    conn.commit()
    conn.close()


def save_message(session_id: str, user_id: str, role: str, content: str):
    """保存一条消息"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_history (session_id, user_id, role, content) VALUES (?, ?, ?, ?)",
        (session_id, user_id, role, content)
    )

    conn.commit()
    conn.close()


def get_history_by_session(session_id: str) -> List[dict]:
    """获取会话的历史消息"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, session_id, user_id, role, content, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "session_id": row[1],
            "user_id": row[2],
            "role": row[3],
            "content": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]


def get_sessions_by_user(user_id: str) -> List[str]:
    """获取用户的会话ID列表"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT session_id FROM chat_history WHERE user_id = ? ORDER BY MAX(created_at) DESC",
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


init_db()
