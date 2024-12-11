import os
import sys
import time
from multiprocessing.pool import ThreadPool
from threading import Timer

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from loguru import logger

from src.main import ICON_PATH
from src.main.python.models import Model, getMotionGroups, getAllExpression
from src.main.python.ollama.Ollama import Ollama
from src.main.python.patFunction.RealtimeRecording import RealtimeRecording
from src.main.python.roles import gl
from src.main.python.windows import getCenterPosition
from src.main.python.windows.ContextManager import ContextManager
from src.main.python.windows.WaveLoader import WaveLoader


class Liv2DWidget(QOpenGLWidget):
    def __init__(self, size: tuple[int, int] = (300, 500), scale: float = 1.0, title: str = "Live2D Widget", iconFileName: str = "icon.jpg", position: tuple[int, int] = (-1, -1)):
        super().__init__(parent=None)
        self.title = title
        self.iconFileName = iconFileName
        self.size = size
        self.scale = scale
        self.iconPath = str(os.path.join(ICON_PATH, iconFileName))
        if not os.path.exists(self.iconPath):
            self.iconPath = str(os.path.join(ICON_PATH, "icon.jpg"))
            logger.warning(f"Icon file {self.iconPath} not found, use default icon instead.")
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayMenu = QMenu(self)

        self.fixSize = (int(size[0] * scale), int(size[1] * scale))

        self.callFunctions: dict[str, callable] = {}
        self.position = position
        if self.position == (-1, -1):
            self.position = getCenterPosition(self.fixSize)
        self.move(*getCenterPosition(self.fixSize))

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(*map(lambda x: int(x * self.scale), self.size))
        self.resize(*map(lambda x: int(x * self.scale), self.size))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if not os.path.exists(self.iconPath):
            self.iconPath = str(os.path.join(ICON_PATH, "icon.jpg"))

    def initTray(self):
        self.trayIcon.setIcon(QIcon(self.iconPath))
        self.trayIcon.setVisible(True)

        show_action = self.trayMenu.addAction("显示")
        show_action.triggered.connect(self.show)
        hide_action = self.trayMenu.addAction("隐藏")
        hide_action.triggered.connect(self.hide)
        exit_action = self.trayMenu.addAction("退出")

        def exit_app():
            self.hide()
            self.trayIcon.setVisible(False)
            self.close()
            sys.exit(0)

        exit_action.triggered.connect(exit_app)

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.setToolTip(self.title)

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
        self.initTray()
        self.show()


class RoleLive2D(Liv2DWidget):
    """
    Live2D角色基类
    提供角色创建继承基类
    """

    def __init__(self, roleName: str,
                 modelName: str,
                 contextManager: ContextManager | None = None,
                 ollama: Ollama | None = None,
                 isLookingAt: bool = True,
                 fps: int = 60,
                 idleFrequency: float = 60.0,
                 size: tuple[int, int] = (300, 500),
                 scale: float = 1.0,
                 title: str = "Live2D Widget",
                 iconFileName: str = "icon.jpg",
                 isAutoBlink: bool = True,
                 isAutoBreath: bool = True,
                 isLog: bool = True,
                 isRecording: bool = True,
                 isAI: bool = True,
                 ollamaArgs: tuple = (),
                 ollamaKwargs: dict = None,
                 recordingArgs: tuple = (),
                 recordingKwargs: dict = None,
                 waveLoaderKwargs: dict = None):
        super().__init__(size=size, scale=scale, title=title, iconFileName=iconFileName)
        self.roleName = roleName
        self.modelName = modelName

        self.model = Model(modelName, isAutoBlink, isAutoBreath, isLog)
        self.idleFrequency = idleFrequency

        self.fps = fps

        self.isInLA = False
        self.clickInLA = False
        self.clickX = -1
        self.clickY = -1

        self.isLookingAt = isLookingAt
        self.contextPosition = (self.position[0] + self.size[0] // 2, self.position[1] + self.height() // 2)
        self.contextManager = contextManager or ContextManager(self, position=self.contextPosition)

        self.isAI = isAI
        self.ollama = None
        if isAI:
            self.ollama = ollama or Ollama(*ollamaArgs, **(ollamaKwargs or {}))

        self.threadPool = ThreadPool(500)

        self.realtimeRecording = RealtimeRecording(*recordingArgs, **(recordingKwargs or {}))
        self.isRecording = isRecording
        self.waveLoader = None
        if self.isRecording:
            kwargs = {"recording": self.realtimeRecording, "waveColor": "blue"}
            kwargs.update({
                "width": int(self.size[0] * self.scale),
                "height": int(self.size[1] * self.scale) // 5,
                "fps": self.fps,
                "position": (int(self.position[0] + self.fixSize[0] / 2 - (int(self.size[0] * self.scale) / 2)),
                             self.position[1] + int(self.size[1] * self.scale))
            })
            kwargs.update(waveLoaderKwargs or {})
            self.waveLoader = WaveLoader(**kwargs)

    def isInL2DArea(self, click_x, click_y):
        return gl.glReadPixels(click_x, self.height() - click_y, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)[3] > 0

    def initializeGL(self):
        super().initializeGL()
        self.model.initialize()
        if self.isRecording:
            self.waveLoader.startRecording()
        self.startTimer(int(1000 / self.fps), Qt.TimerType.PreciseTimer)

    def paintGL(self):
        self.model.paint()

    def resizeGL(self, w, h):
        self.model.resize(w, h)

    def mousePressEvent(self, event):
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.isInL2DArea(x, y):
            self.clickInLA = True
            self.clickX, self.clickY = x, y

    def mouseReleaseEvent(self, event):
        if self.isInLA:
            self.clickInLA = False

    def mouseMoveEvent(self, event):
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.clickInLA:
            self.move(int(self.x() + x - self.clickX), int(self.y() + y - self.clickY))
            self.contextPosition = (int(self.x() + x - self.clickX) + self.width() // 2 - self.contextManager.width() // 2,
                                    int(self.y() + y - self.clickY) + self.height() // 2 - self.contextManager.height() // 2)
            self.contextManager.updatePosition(self.contextPosition)
            if self.realtimeRecording:
                self.waveLoader.move(int(self.waveLoader.x() + x - self.clickX), int(self.waveLoader.y() + y - self.clickY))

    def timerEvent(self, event):
        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        self.isInLA = self.isInL2DArea(local_x, local_y)

        if self.isLookingAt:
            self.model.lookAt(local_x, local_y)

        self.update()

    def __del__(self):
        del self.model

    def loadIdleMotion(self):
        pass

    def loadIdleExpression(self):
        pass

    def loadIdlePose(self):
        pass

    def loadIdleSound(self):
        pass

    def loadStartMotion(self):
        pass

    def eventForMotion(self, callback: callable, group: str, motionName: str, priority: int = 1):
        pass

    def loadMotion(self, group: str, motionName: str, priority: int = 1):
        logger.info(f"Loading motion {motionName} in group {group} with priority {priority}")
        groups: list[str] = getMotionGroups(self.modelName)[group]
        name = f"motions/{motionName}"
        if name in groups:
            self.model.startMotion(group, groups.index(name), priority)
        elif motionName in groups:
            self.model.startMotion(group, groups.index(motionName), priority)
        else:
            logger.warning(f"Motion {motionName} not found in group {group}")

    def loadRandomMotion(self, group: str):
        logger.info(f"Loading random motion in group {group}")
        groups: list[str] = getMotionGroups(self.modelName)[group]
        if len(groups) > 0:
            self.model.startRandomMotion(group, self.idleFrequency)

    def loadExpression(self, expressionName: str):
        if expressionName in getAllExpression(self.modelName):
            self.model.setExpression(expressionName)
        else:
            logger.warning(f"Expression {expressionName} not found in model {self.modelName}")

    def start(self):
        logger.info(f"Starting {self.roleName} with model {self.modelName}")
        self._run()
        self.loadStartMotion()
        Timer(self.idleFrequency, self.loadIdleMotion).start()

    @staticmethod
    def sleep(seconds: float):
        time.sleep(seconds)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = RoleLive2D("独角兽", "dujiaoshou_6", isLookingAt=True, isAutoBlink=True, isAutoBreath=True, isLog=True, ollamaArgs=("llama3.2:latest",))
    widget.start()
    sys.exit(app.exec())
