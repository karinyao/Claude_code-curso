from pathlib import Path
from typing import Optional
from .database import get_connection, DB_PATH


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


# ── Read ───────────────────────────────────────────────────────────────────────

def get_all_todos(status: Optional[str] = None, db_path: Path = DB_PATH) -> list[dict]:
    with get_connection(db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM todos WHERE status = ? ORDER BY id", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_todo_by_id(todo_id: int, db_path: Path = DB_PATH) -> Optional[dict]:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _row_to_dict(row)


# ── Create ─────────────────────────────────────────────────────────────────────

def create_todo(title: str, description: str = "", db_path: Path = DB_PATH) -> dict:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description) VALUES (?, ?)",
            (title, description),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


# ── Update ─────────────────────────────────────────────────────────────────────

def update_todo(todo_id: int, fields: dict, db_path: Path = DB_PATH) -> Optional[dict]:
    if not fields:
        return get_todo_by_id(todo_id, db_path)

    set_clauses = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [todo_id]

    with get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE todos SET {set_clauses}, updated_at = datetime('now') WHERE id = ?",
            values,
        )
        conn.commit()
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _row_to_dict(row)


# ── Delete ─────────────────────────────────────────────────────────────────────

def delete_todo(todo_id: int, db_path: Path = DB_PATH) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return cursor.rowcount > 0
