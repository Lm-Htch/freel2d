import sys
import time
from multiprocessing.pool import ThreadPool

from PySide6.QtCore import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from loguru import logger

from src.main.python.windows import getCenterPosition
from src.main.python.windows.SystemTray import SystemTray


class Liv2DWidget(QOpenGLWidget):
    def __init__(self, size: tuple[int, int] = (300, 500),
                 scale: float = 1.0,
                 title: str = "Live2D Widget",
                 tray: SystemTray = None,
                 trayArgs: tuple = (),
                 trayKwargs: dict = None,
                 position: tuple[int, int] = (-1, -1)):
        super().__init__(parent=None)
        self.title = title
        self.size = size
        self.scale = scale
        try:
            self.tray = tray or SystemTray(*trayArgs, **trayKwargs)
        except FileNotFoundError:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.fixSize = (int(size[0] * scale), int(size[1] * scale))

        self.callFunctions: dict[str, callable] = {}
        self.position = position
        if self.position == (-1, -1):
            logger.debug("Position not set, calculating center position")
            self.position = getCenterPosition(self.fixSize)
        self.move(*self.position)

        self.isRunning = True

        self.threadPool = ThreadPool(500)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(*map(lambda x: int(x * self.scale), self.size))
        self.resize(*map(lambda x: int(x * self.scale), self.size))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tray.init()

    def paintGL(self):
        pass

    def initializeGL(self):
        self.makeCurrent()

    def resizeGL(self, w, h):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def timerEvent(self, event):
        pass

    def wheelEvent(self, event):
        pass

    def keyPressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

    def _run(self):
        self.initUI()
        self.show()

    def timer(self, interval: int | float, exitCondition: callable = lambda: False, callback: callable = lambda: None):
        def run():
            timeSleep = 0
            while self.isRunning and not exitCondition() and timeSleep < interval:
                time.sleep(0.01)
                timeSleep += 0.01
            callback()

        self.threadPool.apply_async(run)

    def exit(self):
        self.isRunning = False
        self.hide()
        self.tray.setVisible(False)
        self.close()
        sys.exit(0)
