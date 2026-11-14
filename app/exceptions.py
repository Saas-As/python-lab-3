"""Собственные исключения приложения.

Все исключения наследуются от базового AppError, чтобы в GUI
можно было ловить их одним except-блоком и показывать пользователю
понятное сообщение.
"""


class AppError(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str = "Произошла ошибка приложения"):
        self.message = message
        super().__init__(self.message)


class ValidationError(AppError):
    """Ошибка валидации входных данных."""


class EmptyTextError(ValidationError):
    """Пустой текст цитаты/факта."""

    def __init__(self):
        super().__init__("Текст не может быть пустым")


class TextTooLongError(ValidationError):
    """Слишком длинный текст."""

    def __init__(self, max_len: int = 500):
        super().__init__(f"Текст не должен превышать {max_len} символов")


class InvalidCategoryError(ValidationError):
    """Неизвестная тематика."""

    def __init__(self, category: str):
        super().__init__(f"Неизвестная тематика: «{category}»")


class InvalidKindError(ValidationError):
    """Неизвестный тип записи (цитата/факт)."""

    def __init__(self, kind: str):
        super().__init__(f"Неизвестный тип записи: «{kind}»")


class DuplicateItemError(AppError):
    """Такая запись уже существует."""

    def __init__(self, text: str):
        preview = text[:40] + ("…" if len(text) > 40 else "")
        super().__init__(f"Такая запись уже есть: «{preview}»")


class ItemNotFoundError(AppError):
    """Запись не найдена по id."""

    def __init__(self, item_id: int):
        super().__init__(f"Запись с id={item_id} не найдена")