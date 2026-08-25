# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "news.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_hash TEXT UNIQUE,
            title_original TEXT,
            title_fa TEXT,
            description_original TEXT,
            description_fa TEXT,
            link TEXT,
            source_name TEXT,
            published_at TEXT,
            fetched_at TEXT,
            sent_to_telegram INTEGER DEFAULT 0
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_published ON news(published_at DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON news(unique_hash)")
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def news_exists(h: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM news WHERE unique_hash=?", (h,))
    ok = c.fetchone() is not None
    conn.close()
    return ok

def insert_news(item: dict) -> bool:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO news (unique_hash, title_original, title_fa, description_original,
                description_fa, link, source_name, published_at, fetched_at, sent_to_telegram)
            VALUES (?,?,?,?,?,?,?,?,?,0)
        """, (
            item["unique_hash"], item["title_original"], item["title_fa"],
            item.get("description_original", ""), item.get("description_fa", ""),
            item["link"], item["source_name"], item["published_at"], item["fetched_at"],
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_latest_news(limit: int = 100):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY published_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_unsent_news(limit: int = 30):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news WHERE sent_to_telegram=0 ORDER BY published_at ASC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def mark_sent(news_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE news SET sent_to_telegram=1 WHERE id=?", (news_id,))
    conn.commit()
    conn.close()

def cleanup_old(days: int = 3):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE published_at < datetime('now', ?)", (f"-{days} days",))
    conn.commit()
    conn.close()
