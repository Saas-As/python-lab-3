"""Тесты для проверки работы репозитория (SQLite)."""

import pytest

from app.exceptions import DuplicateItemError, ItemNotFoundError, NoQuotesInCategoryError
from app.models import Quote
from app.repository import QuoteRepository


@pytest.fixture
def repo():
    """Фикстура: создает чистый репозиторий в памяти для каждого теста."""
    # Передаем ':memory:' вместо пути к файлу quotes.db
    return QuoteRepository(db_path=":memory:")


def test_add_and_get(repo):
    """Проверка добавления и получения записи."""
    item = Quote(text="Тестовая цитата", category="Наука", kind="Цитата", source="Автор")
    added = repo.add(item)

    assert added.id == 1
    assert repo.total() == 1
    
    fetched = repo.get_all()[0]
    assert fetched.text == "Тестовая цитата"
    assert fetched.category == "Наука"


def test_duplicate_error(repo):
    """Проверка, что дубликат выбрасывает исключение."""
    repo.add(Quote(text="Уникальный текст", category="Юмор"))
    
    with pytest.raises(DuplicateItemError):
        repo.add(Quote(text="Уникальный текст", category="Мотивация"))


def test_delete(repo):
    """Проверка удаления записи."""
    item = repo.add(Quote(text="Удаляемая цитата", category="История"))
    repo.delete(item.id)
    
    assert repo.total() == 0
    with pytest.raises(ItemNotFoundError):
        repo.delete(item.id)


def test_get_random_filtered(repo):
    """Проверка генератора с фильтрами."""
    repo.add(Quote(text="Факт 1", category="Наука", kind="Факт"))
    repo.add(Quote(text="Цитата 1", category="Наука", kind="Цитата"))
    repo.add(Quote(text="Цитата 2", category="Юмор", kind="Цитата"))

    # Тест 1: ищем только факты
    item = repo.get_random(kind="Факт")
    assert item.kind == "Факт"

    # Тест 2: ищем только в Юморе
    item = repo.get_random(category="Юмор")
    assert item.category == "Юмор"

    # Тест 3: ищем то, чего нет
    with pytest.raises(NoQuotesInCategoryError):
        repo.get_random(category="Философия") # в базе пусто


def test_count_by_category(repo):
    """Проверка агрегации для графика."""
    repo.add(Quote(text="Ц1", category="Наука"))
    repo.add(Quote(text="Ц2", category="Наука"))
    repo.add(Quote(text="Ц3", category="История"))

    counts = repo.count_by_category()
    assert counts.get("Наука") == 2
    assert counts.get("История") == 1