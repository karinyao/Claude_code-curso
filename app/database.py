import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "todos.db"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                status      TEXT    NOT NULL DEFAULT 'pending',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
