"""Database operations for the todos table."""

import sqlite3
from datetime import datetime, timezone
from typing import Optional


def list_todos(conn: sqlite3.Connection, status: Optional[str] = None) -> list[dict]:
    if status:
        rows = conn.execute(
            "SELECT * FROM todos WHERE status = ? ORDER BY id",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_todo(conn: sqlite3.Connection, todo_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    return dict(row) if row else None


def create_todo(
    conn: sqlite3.Connection,
    title: str,
    description: Optional[str],
) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO todos (title, description, status, created_at) "
        "VALUES (?, ?, 'pending', ?)",
        (title, description, created_at),
    )
    conn.commit()
    return get_todo(conn, cur.lastrowid)


def update_todo(
    conn: sqlite3.Connection,
    todo_id: int,
    fields: dict,
) -> Optional[dict]:
    if not fields:
        return get_todo(conn, todo_id)

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [todo_id]
    cur = conn.execute(
        f"UPDATE todos SET {set_clause} WHERE id = ?", values
    )
    conn.commit()
    if cur.rowcount == 0:
        return None
    return get_todo(conn, todo_id)


def delete_todo(conn: sqlite3.Connection, todo_id: int) -> bool:
    cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    return cur.rowcount > 0
