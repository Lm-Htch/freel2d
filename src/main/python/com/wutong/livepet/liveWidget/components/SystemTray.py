import os.path

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu

from src import ICON_PATH
from src.main.python.com.wutong.livepet.liveWidget import LiveWidget
from src.main.python.com.wutong.livepet.liveWidget.components.Component import Component
from src.main.python.com.wutong.livepet.widgets.PetWidget import PetWidget


class SystemTray(QSystemTrayIcon, Component):
    """
    系统托盘组件
    实现了显示/隐藏桌宠、退出桌宠功能
    """

    def __init__(self, tooltiptext: str = "LivePet"):
        """
        初始化系统托盘组件
        :param tooltiptext: 托盘图标提示文本
        """
        super().__init__(componentName=__name__)

        self.setToolTip(tooltiptext)
        self.setIcon(QIcon(os.path.join(ICON_PATH, "icon.jpg")))

        self.liveWidget: LiveWidget | None = None

        self.trayMenu: QMenu | None = None

        self.trayActions: dict[str, QAction] = {}

    def exitLivePet(self):
        """
        退出桌宠
        :return:
        """
        self.setVisible(False)
        self.liveWidget.close()

    def switchPetDisplay(self):
        """
        隐藏桌宠
        :return:
        """
        if self.liveWidget.isHidden():
            self.liveWidget.show()
            self.setNewActionName("显示桌宠", "隐藏桌宠")
        else:
            self.liveWidget.hide()
            self.setNewActionName("隐藏桌宠", "显示桌宠")

    def switchLookingAt(self):
        """
        切换鼠标跟随
        :return:
        """
        if isinstance(self.liveWidget, PetWidget):
            if self.liveWidget.isLookingAt:
                self.setNewActionName("取消鼠标跟随", "鼠标跟随")
            else:
                self.setNewActionName("鼠标跟随", "取消鼠标跟随")
            self.liveWidget.isLookingAt = self.liveWidget.isLookingAt ^ True

    def init(self):
        self.trayMenu = QMenu()
        self.setVisible(True)

        for action in self.trayActions.values():
            self.liveWidget.logger.info(f"Add tray action {action.text()}.")
            self.trayMenu.addAction(action)

        self.setContextMenu(self.trayMenu)
        self.liveWidget.logger.success("Tray menu loaded.")

    def componentRunnable(self, liveWidget: LiveWidget) -> bool:
        self.liveWidget = liveWidget
        self.addTrayAction("隐藏桌宠", self.switchPetDisplay)
        if isinstance(liveWidget, PetWidget):
            if liveWidget.isLookingAt:
                self.addTrayAction("取消鼠标跟随", self.switchLookingAt)
            else:
                self.addTrayAction("鼠标跟随", self.switchLookingAt)

        self.addTrayAction("退出桌宠", self.exitLivePet)
        self.init()
        return True

    def addTrayAction(self, actionName: str, actionFunc: callable):
        self.trayActions[actionName] = QAction(actionName, self)
        self.trayActions[actionName].triggered.connect(actionFunc)

    def setTrayActionCall(self, actionName: str, newActionFunc: callable):
        if actionName in self.trayActions:
            self.trayActions[actionName].triggered.disconnect()
            self.trayActions[actionName].triggered.connect(newActionFunc)
        else:
            self.liveWidget.logger.warning(f"Tray action {actionName} not found, cannot set call function.")

    def setNewActionName(self, oldActionName: str, newActionName: str):
        if oldActionName in self.trayActions:
            self.trayActions[newActionName] = self.trayActions.pop(oldActionName)
            self.trayActions[newActionName].setText(newActionName)
        else:
            self.liveWidget.logger.warning(f"Tray action {oldActionName} not found, cannot set new name.")

    def componentRelease(self) -> bool:
        self.setVisible(False)
        return True
