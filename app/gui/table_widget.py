"""Таблица записей (цитат/фактов)."""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt

from app.models import Quote


class QuoteTableWidget(QTableWidget):
    """Таблица с колонками ID, Текст, Тематика, Тип, Источник."""

    HEADERS = ("ID", "Текст", "Тематика", "Тип", "Источник")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 380)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 70)

    def load(self, items: list[Quote]) -> None:
        """Полностью перерисовывает таблицу из списка записей."""
        self.setRowCount(0)
        for row, q in enumerate(items):
            self.insertRow(row)
            self.setItem(row, 0, self._cell(str(q.id)))
            self.setItem(row, 1, self._cell(q.short_text(80)))
            self.setItem(row, 2, self._cell(q.category))
            self.setItem(row, 3, self._cell(q.kind))
            self.setItem(row, 4, self._cell(q.source or "—"))

    def selected_id(self) -> int | None:
        """Возвращает id выделенной строки или None."""
        row = self.currentRow()
        if row < 0:
            return None
        item = self.item(row, 0)
        return int(item.text()) if item else None

    @staticmethod
    def _cell(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item