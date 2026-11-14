"""Модели данных: цитата/факт и справочники тематик/типов."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import ClassVar

from app.exceptions import (
    EmptyTextError,
    TextTooLongError,
    InvalidCategoryError,
    InvalidKindError,
)


# Справочники (используются в QComboBox и для валидации)
CATEGORIES: tuple[str, ...] = (
    "Наука",
    "Мотивация",
    "История",
    "Юмор",
    "Философия",
    "Факты о мире",
)

KINDS: tuple[str, ...] = ("Цитата", "Факт")

MAX_TEXT_LEN: int = 500
MAX_SOURCE_LEN: int = 100


@dataclass
class Quote:
    """Запись: цитата или факт с тематикой и источником.

    Attributes:
        id:         уникальный идентификатор (присваивается репозиторием)
        text:       сам текст цитаты/факта
        category:   тематика (из CATEGORIES)
        source:     автор / источник (может быть пустым)
        kind:       "Цитата" или "Факт"
        created_at: момент добавления (ISO-строка для сериализации)
    """

    text: str
    category: str
    kind: str = "Цитата"
    source: str = ""
    id: int = field(default=0)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    _CATEGORIES: ClassVar[tuple[str, ...]] = CATEGORIES
    _KINDS: ClassVar[tuple[str, ...]] = KINDS

    def __post_init__(self) -> None:
        self.validate()

    # ---------- валидация ----------

    def validate(self) -> None:
        """Проверяет корректность полей. Бросает ValidationError-наследников."""
        self.text = (self.text or "").strip()
        self.source = (self.source or "").strip()

        if not self.text:
            raise EmptyTextError()
        if len(self.text) > MAX_TEXT_LEN:
            raise TextTooLongError(MAX_TEXT_LEN)
        if self.category not in self._CATEGORIES:
            raise InvalidCategoryError(self.category)
        if self.kind not in self._KINDS:
            raise InvalidKindError(self.kind)
        if len(self.source) > MAX_SOURCE_LEN:
            raise TextTooLongError(MAX_SOURCE_LEN)

    # ---------- утилиты ----------

    def to_dict(self) -> dict:
        """Сериализация в dict (пригодится на Medium, когда появится БД)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        """Десериализация из dict."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def short_text(self, limit: int = 60) -> str:
        """Короткая версия текста для таблицы."""
        return self.text if len(self.text) <= limit else self.text[:limit - 1] + "…"