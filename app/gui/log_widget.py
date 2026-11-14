"""Виджет лога активности (только для чтения)."""

from datetime import datetime

from PySide6.QtWidgets import QPlainTextEdit


class LogWidget(QPlainTextEdit):
    """Простой лог: сообщения дописываются в конец, автоскролл вниз."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Здесь будет история действий…")
        self.setMaximumBlockCount(500)  # чтобы не рос бесконечно

    def log(self, message: str) -> None:
        """Добавляет запись с отметкой времени."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.appendPlainText(f"[{ts}] {message}")
        # QPlainTextEdit автоматически скроллит вниз при appendPlainText