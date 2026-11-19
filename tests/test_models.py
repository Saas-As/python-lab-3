"""Тесты для проверки валидации моделей."""

import pytest

from app.exceptions import EmptyTextError, InvalidCategoryError, TextTooLongError
from app.models import Quote, MAX_TEXT_LEN


def test_valid_quote():
    """Корректная запись создается без ошибок."""
    q = Quote(text="Валидный текст", category="Наука", kind="Цитата")
    assert q.text == "Валидный текст"


def test_empty_text_error():
    """Пустой текст или пробелы вызывают ошибку."""
    with pytest.raises(EmptyTextError):
        Quote(text="   ", category="Наука")
        
    with pytest.raises(EmptyTextError):
        Quote(text="", category="Наука")


def test_text_too_long_error():
    """Текст больше лимита вызывает ошибку."""
    long_text = "А" * (MAX_TEXT_LEN + 1)
    with pytest.raises(TextTooLongError):
        Quote(text=long_text, category="Наука")


def test_invalid_category_error():
    """Несуществующая категория вызывает ошибку."""
    with pytest.raises(InvalidCategoryError):
        Quote(text="Текст", category="Кулинария")