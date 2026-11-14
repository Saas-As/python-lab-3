"""Точка входа приложения «Генератор цитат и фактов»."""

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="app.log",
    encoding="utf-8",
)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("QuoteFactGenerator")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())