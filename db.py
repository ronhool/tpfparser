import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Tuple, Dict, Any

from config import DB_PATH, FRESHNESS_DAYS


def compute_hash(title: str, url: str, snippet: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(title.encode("utf-8"))
    hasher.update(url.encode("utf-8"))
    hasher.update(snippet.encode("utf-8"))
    return hasher.hexdigest()


@contextmanager
def get_conn(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class NewsDB:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._init_db()

    def _init_db(self):
        with get_conn(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    pub_date TEXT,
                    tags TEXT,
                    content_snippet TEXT,
                    hash TEXT UNIQUE
                )
                """
            )
            conn.commit()

    def add_news(self, items: Iterable[Dict[str, Any]]) -> int:
        inserted = 0
        with get_conn(self.path) as conn:
            for item in items:
                try:
                    conn.execute(
                        """
                        INSERT INTO news (title, url, pub_date, tags, content_snippet, hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            item["title"],
                            item["url"],
                            item.get("pub_date"),
                            ",".join(item.get("tags", [])),
                            item.get("content_snippet", ""),
                            item["hash"],
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    # Duplicate hash; skip
                    continue
            conn.commit()
        return inserted

    def recent_news(self, days: int = FRESHNESS_DAYS) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        with get_conn(self.path) as conn:
            cursor = conn.execute(
                """
                SELECT id, title, url, pub_date, tags, content_snippet, hash
                FROM news
                WHERE pub_date IS NULL OR datetime(pub_date) >= ?
                ORDER BY datetime(pub_date) DESC
                """,
                (cutoff.isoformat(),),
            )
            return [dict(row) for row in cursor.fetchall()]

    def exists_hash(self, content_hash: str) -> bool:
        with get_conn(self.path) as conn:
            cursor = conn.execute("SELECT 1 FROM news WHERE hash = ? LIMIT 1", (content_hash,))
            return cursor.fetchone() is not None

    def latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        with get_conn(self.path) as conn:
            cursor = conn.execute(
                """
                SELECT id, title, url, pub_date, tags, content_snippet, hash
                FROM news
                ORDER BY datetime(pub_date) DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

