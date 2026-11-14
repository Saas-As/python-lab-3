"""Главное окно приложения."""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.data.seed import SEED_DATA
from app.exceptions import AppError
from app.gui.chart_widget import ActivityChartWidget
from app.gui.log_widget import LogWidget
from app.gui.table_widget import QuoteTableWidget
from app.models import CATEGORIES, KINDS, Quote
from app.repository import QuoteRepository

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Главное окно: форма ввода, таблица, график, лог, меню."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Генератор цитат и фактов")
        self.resize(1100, 750)

        self.repo = QuoteRepository()
        self.repo.bulk_add(SEED_DATA)

        self._build_ui()
        self._build_menu()
        self._refresh_all()
        self.log_widget.log(f"Загружено стартовых записей: {self.repo.total()}")

    # ---------- UI ----------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        # --- Форма добавления ---
        form_box = QGroupBox("Добавить запись")
        form_layout = QFormLayout(form_box)

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Текст цитаты или факта…")
        self.input_text.setMaxLength(500)

        self.input_category = QComboBox()
        self.input_category.addItems(CATEGORIES)

        self.input_kind = QComboBox()
        self.input_kind.addItems(KINDS)

        self.input_source = QLineEdit()
        self.input_source.setPlaceholderText("Автор / источник (необязательно)")
        self.input_source.setMaxLength(100)

        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self._on_add_clicked)

        self.btn_delete = QPushButton("Удалить выбранное")
        self.btn_delete.clicked.connect(self._on_delete_clicked)

        form_layout.addRow("Текст:", self.input_text)
        form_layout.addRow("Тематика:", self.input_category)
        form_layout.addRow("Тип:", self.input_kind)
        form_layout.addRow("Источник:", self.input_source)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_delete)
        buttons.addStretch()
        form_layout.addRow(buttons)

        root.addWidget(form_box)

        # --- Генератор ---
        gen_box = QGroupBox("Генератор")
        gen_layout = QHBoxLayout(gen_box)

        self.gen_category = QComboBox()
        self.gen_category.addItems(["Любая"] + list(CATEGORIES))

        self.gen_kind = QComboBox()
        self.gen_kind.addItems(["Любой"] + list(KINDS))

        self.btn_generate = QPushButton("Сгенерировать")
        self.btn_generate.clicked.connect(self._on_generate_clicked)

        self.gen_result = QLabel("Нажмите «Сгенерировать», чтобы получить цитату или факт")
        self.gen_result.setWordWrap(True)
        self.gen_result.setStyleSheet("font-size: 16px; padding: 10px; "
                                    "border: 1px solid #888; border-radius: 6px;")

        gen_layout.addWidget(QLabel("Тематика:"))
        gen_layout.addWidget(self.gen_category)
        gen_layout.addWidget(QLabel("Тип:"))
        gen_layout.addWidget(self.gen_kind)
        gen_layout.addWidget(self.btn_generate)
        gen_layout.addWidget(self.gen_result, stretch=1)

        root.addWidget(gen_box)

        # --- Таблица ---
        self.table = QuoteTableWidget()

        # --- Правая панель: график + лог ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.chart = ActivityChartWidget()
        self.log_widget = LogWidget()

        right_layout.addWidget(self.chart, stretch=3)
        right_layout.addWidget(QLabel("Лог активности:"))
        right_layout.addWidget(self.log_widget, stretch=2)

        # --- Splitter: таблица | график+лог ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.table)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([650, 450])

        root.addWidget(splitter, stretch=1)

        self.statusBar().showMessage("Готово")

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ---------- обработчики ----------

    def _on_add_clicked(self) -> None:
        try:
            item = Quote(
                text=self.input_text.text(),
                category=self.input_category.currentText(),
                kind=self.input_kind.currentText(),
                source=self.input_source.text(),
            )
            self.repo.add(item)
        except AppError as e:
            QMessageBox.warning(self, "Ошибка добавления", e.message)
            self.log_widget.log(f"Ошибка: {e.message}")
            return
        except Exception as e:  # страховка
            logger.exception("Необработанная ошибка при добавлении")
            QMessageBox.critical(self, "Критическая ошибка", str(e))
            return

        self.log_widget.log(
            f"Добавлено [{item.kind}] «{item.short_text(40)}» — {item.category}"
        )
        self._clear_inputs()
        self._refresh_all()

    def _on_delete_clicked(self) -> None:
        item_id = self.table.selected_id()
        if item_id is None:
            QMessageBox.information(self, "Удаление", "Сначала выберите строку в таблице.")
            return
        try:
            self.repo.delete(item_id)
        except AppError as e:
            QMessageBox.warning(self, "Ошибка удаления", e.message)
            self.log_widget.log(f"Ошибка удаления: {e.message}")
            return

        self.log_widget.log(f"Удалена запись id={item_id}")
        self._refresh_all()

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Генератор цитат и фактов с выбором тематики.\n\n"
            "Лабораторная работа №3, вариант 10.\n"
            "Сложность: Rare.\n\n"
            "Стек: Python + PySide6.",
        )

    def _on_generate_clicked(self) -> None:
        category = self.gen_category.currentText()
        kind = self.gen_kind.currentText()
        try:
            q = self.repo.get_random(
                category=None if category == "Любая" else category,
                kind=None if kind == "Любой" else kind,
            )
        except AppError as e:
            QMessageBox.information(self, "Генерация", e.message)
            self.log_widget.log(f"Генерация не удалась: {e.message}")
            return
        self.gen_result.setText(f"«{q.text}»\n— {q.source or 'без источника'} ({q.category}, {q.kind})")
        self.log_widget.log(f"Сгенерировано: [{q.kind}] «{q.short_text(40)}» — {q.category}")

    # ---------- обновление ----------

    def _clear_inputs(self) -> None:
        self.input_text.clear()
        self.input_source.clear()
        self.input_text.setFocus()

    def _refresh_all(self) -> None:
        items = self.repo.get_all()
        self.table.load(items)
        self.chart.update_data(self.repo.count_by_category())
        self.statusBar().showMessage(f"Всего записей: {len(items)}")