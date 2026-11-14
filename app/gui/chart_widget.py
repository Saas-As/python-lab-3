"""График активности: сколько записей в каждой тематике."""

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.models import CATEGORIES


class ActivityChartWidget(QWidget):
    """Столбчатая диаграмма по тематикам (обновляется извне)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._chart = QChart()
        self._chart.setTitle("Активность по тематикам")
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self._chart.legend().setVisible(False)

        self._view = QChartView(self._chart)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)

        self._series: QBarSeries | None = None
        self._axis_x: QBarCategoryAxis | None = None
        self._axis_y: QValueAxis | None = None

    def update_data(self, counts: dict[str, int]) -> None:
        """Перестраивает график по словарю {тематика: количество}."""
        if self._series is not None:
            self._chart.removeSeries(self._series)
        if self._axis_x is not None:
            self._chart.removeAxis(self._axis_x)
        if self._axis_y is not None:
            self._chart.removeAxis(self._axis_y)

        # Всегда показываем все тематики, даже с нулём
        values = [counts.get(cat, 0) for cat in CATEGORIES]

        bar_set = QBarSet("Записей")
        bar_set.append(values)

        self._series = QBarSeries()
        self._series.append(bar_set)
        self._chart.addSeries(self._series)

        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(list(CATEGORIES))
        self._chart.addAxis(self._axis_x, Qt.AlignmentFlag.AlignBottom)
        self._series.attachAxis(self._axis_x)

        max_val = max(values) if any(values) else 1
        self._axis_y = QValueAxis()
        self._axis_y.setRange(0, max_val + 1)
        self._axis_y.setLabelFormat("%d")
        self._axis_y.setTitleText("Количество")
        self._chart.addAxis(self._axis_y, Qt.AlignmentFlag.AlignLeft)
        self._series.attachAxis(self._axis_y)