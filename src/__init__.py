import sys

from PySide6.QtWidgets import QApplication

from src.main.python.roles.Hiyori import Hiyori
from src.main.python.roles.Lafei import Lafei


def main():
    app = QApplication(sys.argv)
    Lafei().start()
    exit(app.exec())
