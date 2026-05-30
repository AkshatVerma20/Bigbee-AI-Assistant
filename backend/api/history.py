from fastapi import APIRouter
from sqlalchemy import create_engine, text
from backend.config import settings
import os

router = APIRouter()

os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)
engine = create_engine(f"sqlite:///{settings.sqlite_db_path}", echo=False)

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.commit()


@router.get("/history/{user_id}/{session_id}")
def get_history(user_id: str, session_id: str, limit: int = 50):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT role, content, timestamp FROM chat_history
            WHERE user_id = :uid AND session_id = :sid
            ORDER BY timestamp DESC LIMIT :limit
        """), {"uid": user_id, "sid": session_id, "limit": limit}).fetchall()
    return {"messages": [dict(r._mapping) for r in reversed(rows)]}


@router.post("/history/{user_id}/{session_id}")
def save_message(user_id: str, session_id: str, role: str, content: str):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO chat_history (user_id, session_id, role, content)
            VALUES (:uid, :sid, :role, :content)
        """), {"uid": user_id, "sid": session_id, "role": role, "content": content})
        conn.commit()
    return {"status": "saved"}


@router.delete("/history/{user_id}/{session_id}")
def clear_history(user_id: str, session_id: str):
    with engine.connect() as conn:
        conn.execute(text("""
            DELETE FROM chat_history WHERE user_id = :uid AND session_id = :sid
        """), {"uid": user_id, "sid": session_id})
        conn.commit()
    return {"status": "cleared"}
