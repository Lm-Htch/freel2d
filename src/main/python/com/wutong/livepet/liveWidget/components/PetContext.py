from threading import Timer

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QStyleOption, QStyle

from src.main.python.com.wutong.livepet.liveWidget import LiveWidget
from src.main.python.com.wutong.livepet.liveWidget.components import Component
from src.main.python.com.wutong.livepet.liveWidget.components.SystemTray import SystemTray
from src.main.python.com.wutong.livepet.widgets.PetWidget import PetWidget


class PetContext(QWidget, Component):
    def __init__(self,
                 systemTray: SystemTray,
                 width: int,
                 height: int,
                 positionX: int,
                 positionY: int,
                 showTime: int = 30,
                 backgroundColor: tuple[int, int, int, float] = (0, 0, 0, 50),
                 textColor: tuple[int, int, int] | str = "white",
                 fontSize: int = 16,
                 fontFamily: str = "微软雅黑",
                 borderRadius: int = 10):
        """
        初始化
        :param width: 宽度
        :param height: 高度
        :param positionX: X坐标
        :param positionY: Y坐标
        """
        super().__init__(componentName=__name__)
        self.systemTray = systemTray
        self.width = width
        self.height = height
        self.positionX = positionX
        self.positionY = positionY
        self.showTime = showTime

        self.liveWidget: LiveWidget | PetWidget | None = None

        self.label: QLabel | None = None

        self.labelQss = f"color: {textColor};" \
                        f"font-size: {fontSize}px;" \
                        f"font-family: {fontFamily}; " \
                        f"background-color: rgba{backgroundColor}; " \
                        f"border-radius: {borderRadius}px;"

        self.clickX = -1
        self.clickY = -1

        self.isShowing = False

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def initUI(self):
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setGeometry(0, 0, self.width, self.height)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(self.labelQss)
        self.setParent(self.liveWidget)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.clickX = self.liveWidget.clickX
        self.clickY = self.liveWidget.clickY
        self.setGeometry(self.positionX, self.positionY, self.width, self.height)
        self.setVisible(True)

    def switchShowAndHide(self):
        if self.isVisible():
            self.hide()
            self.systemTray.setNewActionName("关闭桌宠气泡", "打开桌宠气泡")
        else:
            self.show()
            self.systemTray.setNewActionName("打开桌宠气泡", "关闭桌宠气泡")

    def addTray(self):
        self.systemTray.addTrayAction("关闭桌宠气泡", self.switchShowAndHide)

    def componentRunnable(self, liveWidget: LiveWidget) -> bool:
        self.liveWidget = liveWidget
        self.initUI()
        self.addTray()
        self.liveWidget.logger.success("PetContext runnable")
        return True

    def componentRelease(self) -> bool:
        self.close()
        return True

    def componentShow(self):
        if self.liveWidget:
            self.show()

    def componentHide(self):
        self.hide()

    def componentMove(self, event: QMouseEvent) -> None:
        self.positionX = self.liveWidget.positionX
        self.positionY = self.liveWidget.positionY - self.height
        self.move(self.positionX, self.positionY)

    def showText(self, text: str):
        if not self.isShowing:
            Timer(self.showTime, self.clearText).start()
        self.isShowing = True
        self.liveWidget.logger.info(f"PetContext showText: {text}")
        self.label.setText(text)

    def addText(self, text: str):
        self.show()
        self.label.setText(self.label.text() + text)

    def clearText(self):
        self.liveWidget.logger.info("PetContext clearText")
        self.label.setText("")
        self.isShowing = False
