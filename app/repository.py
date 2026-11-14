"""In-memory репозиторий записей.

На сложности Medium заменим на SQLite-реализацию с тем же интерфейсом,
поэтому все обращения к данным идут только через этот класс.
"""

from collections import Counter
from typing import Iterable

from app.exceptions import DuplicateItemError, ItemNotFoundError, NoQuotesInCategoryError
from app.models import Quote
import random

class QuoteRepository:
    """Хранилище цитат и фактов в памяти."""

    def __init__(self) -> None:
        self._items: list[Quote] = []
        self._counter: int = 0
        self._seen_texts: set[str] = set()

    # ---------- CRUD ----------

    def add(self, item: Quote) -> Quote:
        """Добавляет запись, присваивает id. Бросает DuplicateItemError."""
        key = item.text.casefold()
        if key in self._seen_texts:
            raise DuplicateItemError(item.text)

        self._counter += 1
        item.id = self._counter
        self._items.append(item)
        self._seen_texts.add(key)
        return item

    def get_all(self) -> list[Quote]:
        """Все записи (в порядке добавления)."""
        return list(self._items)

    def get_by_category(self, category: str) -> list[Quote]:
        """Записи указанной тематики."""
        return [q for q in self._items if q.category == category]

    def get_by_id(self, item_id: int) -> Quote:
        """Запись по id. Бросает ItemNotFoundError."""
        for q in self._items:
            if q.id == item_id:
                return q
        raise ItemNotFoundError(item_id)

    def delete(self, item_id: int) -> None:
        """Удаляет запись по id. Бросает ItemNotFoundError."""
        for i, q in enumerate(self._items):
            if q.id == item_id:
                self._items.pop(i)
                self._seen_texts.discard(q.text.casefold())
                return
        raise ItemNotFoundError(item_id)

    def clear(self) -> None:
        """Полностью очищает репозиторий (удобно в тестах)."""
        self._items.clear()
        self._seen_texts.clear()
        self._counter = 0

    # ---------- агрегаты ----------

    def count_by_category(self) -> dict[str, int]:
        """Сколько записей в каждой тематике (для графика)."""
        counter = Counter(q.category for q in self._items)
        return dict(counter)

    def count_by_kind(self) -> dict[str, int]:
        """Сколько цитат и фактов."""
        counter = Counter(q.kind for q in self._items)
        return dict(counter)

    def total(self) -> int:
        """Общее количество записей."""
        return len(self._items)

    def bulk_add(self, items: Iterable[Quote]) -> int:
        """Добавляет несколько записей, возвращает число успешно добавленных."""
        added = 0
        for item in items:
            try:
                self.add(item)
                added += 1
            except DuplicateItemError:
                continue
        return added

    def get_random(self, category: str | None = None, kind: str | None = None) -> Quote:
        """Возвращает случайную запись. Фильтры опциональны."""
        pool = self._items
        if category:
            pool = [q for q in pool if q.category == category]
        if kind:
            pool = [q for q in pool if q.kind == kind]
        if not pool:
            raise NoQuotesInCategoryError(category or "все")
        return random.choice(pool)