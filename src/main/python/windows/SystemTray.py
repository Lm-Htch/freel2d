import os.path

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from loguru import logger

from src.main import ICON_PATH


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None, icon: QIcon | str = "icon.jpg", tooltip: str = None, menu: QMenu = None):
        super().__init__(parent)
        if isinstance(icon, str):
            self.iconPng = icon
            self.iconPath = os.path.join(ICON_PATH, self.iconPng)
            if not os.path.exists(self.iconPath):
                logger.warning(f"Icon file {self.iconPath} not found, using default icon.")
                self.iconPath = os.path.join(ICON_PATH, "icon.jpg")
                if not os.path.exists(self.iconPath):
                    logger.error(f"Default icon file {self.iconPath} not found, using default icon.")
                    raise FileNotFoundError(f"Icon file {self.iconPath} not found.")
            self.setIcon(QIcon(self.iconPath))
        else:
            self.setIcon(icon)
            self.iconPng = icon.name()

        self.setToolTip(tooltip or "System Tray")

        self.trayMenu = menu or QMenu(parent)

        self.trayActions: dict[str, QAction] = {}

    def init(self):
        logger.info(f"Init system tray icon {self.iconPng}.")
        self.setVisible(True)

        for action in self.trayActions.values():
            logger.info(f"Add tray action {action.text()}.")
            self.trayMenu.addAction(action)

        self.setContextMenu(self.trayMenu)

    def addTrayAction(self, actionName: str, actionFunc: callable):
        self.trayActions[actionName] = QAction(actionName, self)
        self.trayActions[actionName].triggered.connect(actionFunc)

    def setTrayActionCall(self, actionName: str, newActionFunc: callable):
        if actionName in self.trayActions:
            self.trayActions[actionName].triggered.disconnect()
            self.trayActions[actionName].triggered.connect(newActionFunc)
        else:
            logger.warning(f"Tray action {actionName} not found, cannot set call function.")

    def setNewActionName(self, oldActionName: str, newActionName: str):
        if oldActionName in self.trayActions:
            self.trayActions[newActionName] = self.trayActions.pop(oldActionName)
            self.trayActions[newActionName].setText(newActionName)
        else:
            logger.warning(f"Tray action {oldActionName} not found, cannot set new name.")
