import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict


class DataBase:
    """Basic database handler for memoizing article workflow."""

    def _normalize_keywords(self, keywords: List[str] | str) -> str:
        """
        Normalize keywords to a stable, comparable cache key.
        - Accepts list or string.
        - Lowercases, strips, deduplicates, sorts.
        - Joins by comma.
        """
        if isinstance(keywords, str):
            parts = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        else:
            parts = [str(k).strip().lower() for k in keywords if str(k).strip()]
        parts = sorted(set(parts))
        return ",".join(parts)

    def _db_path(self) -> str:
        resources_dir = Path(__file__).absolute().parent / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        return (resources_dir / "news_cache.sqlite").as_posix()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path())
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS articles_cache (
                which TEXT NOT NULL,
                keyword TEXT NOT NULL,
                articles_json TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (which, keyword)
            );
            """
        )
        return conn

    def get_cached_articles(self, which: str, keywords: List[str] | str) -> Optional[List[Dict]]:
        key = self._normalize_keywords(keywords)
        with self._get_conn() as conn:
            cur = conn.execute(
                "SELECT articles_json FROM articles_cache WHERE which = ? AND keyword = ?;",
                (which, key),
            )
            row = cur.fetchone()
            if not row:
                return None
            try:
                payload = json.loads(row[0])
                if isinstance(payload, list):
                    return payload
                # If we stored the whole response by mistake, try to pull `.articles`
                if isinstance(payload, dict) and "articles" in payload:
                    return payload["articles"]
            except Exception:
                return None
        return None

    def set_cached_articles(self, which: str, keywords: List[str] | str, articles: List[Dict]) -> None:
        key = self._normalize_keywords(keywords)
        payload = json.dumps(articles)
        try:
            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO articles_cache (which, keyword, articles_json)
                    VALUES (?, ?, ?)
                    ON CONFLICT(which, keyword) DO UPDATE SET
                        articles_json = excluded.articles_json,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (which, key, payload),
                )
        except Exception as e:
            print("Encountered exception when attemping to save articles.")
            raise e
