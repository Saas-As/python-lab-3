"""Репозиторий записей с хранением в базе данных SQLite."""

import sqlite3
from collections import Counter
from pathlib import Path

from app.exceptions import DuplicateItemError, ItemNotFoundError
from app.models import Quote

# Файл базы данных будет создан рядом с main.py
DB_PATH = Path("quotes.db")


class QuoteRepository:
    """Хранилище цитат и фактов в SQLite."""

    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # позволяет обращаться к колонкам по имени
        return conn

    def _init_db(self) -> None:
        """Создает таблицу, если ее еще нет."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source TEXT,
                    created_at TEXT NOT NULL
                )
            """)

    # ---------- CRUD ----------

    def add(self, item: Quote) -> Quote:
        """Добавляет запись в БД."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO quotes (text, category, kind, source, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (item.text, item.category, item.kind, item.source, item.created_at)
                )
                item.id = cursor.lastrowid
                return item
        except sqlite3.IntegrityError:
            # TEXT UNIQUE выбросит IntegrityError при дубликате
            raise DuplicateItemError(item.text)

    def get_all(self) -> list[Quote]:
        """Возвращает все записи."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM quotes ORDER BY id").fetchall()
            return [Quote.from_dict(dict(row)) for row in rows]

    def get_by_category(self, category: str) -> list[Quote]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM quotes WHERE category = ?", (category,)).fetchall()
            return [Quote.from_dict(dict(row)) for row in rows]

    def get_by_id(self, item_id: int) -> Quote:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM quotes WHERE id = ?", (item_id,)).fetchone()
            if not row:
                raise ItemNotFoundError(item_id)
            return Quote.from_dict(dict(row))

    def delete(self, item_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM quotes WHERE id = ?", (item_id,))
            if cursor.rowcount == 0:
                raise ItemNotFoundError(item_id)

    # ---------- Агрегаты (для графика) ----------

    def count_by_category(self) -> dict[str, int]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT category, COUNT(*) as cnt FROM quotes GROUP BY category").fetchall()
            return {row["category"]: row["cnt"] for row in rows}

    def count_by_kind(self) -> dict[str, int]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT kind, COUNT(*) as cnt FROM quotes GROUP BY kind").fetchall()
            return {row["kind"]: row["cnt"] for row in rows}

    def total(self) -> int:
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM quotes").fetchone()
            return row["cnt"]

    def bulk_add(self, items: list[Quote]) -> int:
        added = 0
        for item in items:
            try:
                # Проверяем, есть ли уже такой текст, чтобы не было ошибки при первом запуске
                with self._get_connection() as conn:
                    exists = conn.execute("SELECT 1 FROM quotes WHERE text = ?", (item.text,)).fetchone()
                    if not exists:
                        self.add(item)
                        added += 1
            except DuplicateItemError:
                continue
        return added

    def get_random(self, category: str | None = None, kind: str | None = None) -> Quote:
        """Возвращает случайную запись из БД с учетом фильтров."""
        query = "SELECT * FROM quotes"
        params = []
        conditions = []
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        if kind:
            conditions.append("kind = ?")
            params.append(kind)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY RANDOM() LIMIT 1"
        
        with self._get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            if not row:
                from app.exceptions import NoQuotesInCategoryError
                raise NoQuotesInCategoryError(category or "выбранным фильтрам")
            return Quote.from_dict(dict(row))