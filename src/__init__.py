import os
import sys

from PySide6.QtWidgets import QApplication

from src.main import CONFIG_PATH
from src.main.python.roles.Hiyori import Hiyori
from src.main.python.roles.Lafei import Lafei
from src.main.python.roles.RoleLive2D import loadRoleFromConfig


def main():
    app = QApplication(sys.argv)
    if os.path.exists(os.path.join(CONFIG_PATH, "Lafei.json")):
        loadRoleFromConfig("Lafei.json", Lafei).start()
    else:
        Lafei().start()
    exit(app.exec())
