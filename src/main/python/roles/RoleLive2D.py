import sys
import time
from typing import Type

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication
from loguru import logger

from src.main.python.models import Model, getMotionGroups, getAllExpression
from src.main.python.ollama.Ollama import Ollama
from src.main.python.patFunction.RealtimeRecording import RealtimeRecording
from src.main.python.roles import gl
from src.main.python.windows import saveToConfigureFile, loadFromConfigureFile
from src.main.python.windows.ContextManager import ContextManager
from src.main.python.windows.Liv2DWidget import Liv2DWidget
from src.main.python.windows.WaveLoader import WaveLoader


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
                 isAI: bool = True,
                 isRecording: bool = True,
                 ollamaArgs: tuple = (),
                 ollamaKwargs: dict = None,
                 recordingArgs: tuple = (),
                 recordingKwargs: dict = None,
                 trayArgs: tuple = (),
                 trayKwargs=None,
                 waveLoaderKwargs: dict = None,
                 position: tuple[int, int] = None,
                 contextPosition: tuple[int, int] = None,
                 waveLoaderPosition: tuple[int, int] = None,
                 fromConfigureFile: bool = False):
        super().__init__(size=size,
                         scale=scale,
                         title=title,
                         trayArgs=trayArgs or (),
                         trayKwargs=trayKwargs or {"icon": iconFileName if iconFileName != "" else "icon.jpg", "tooltip": title},
                         position=position or (-1, -1))
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
        self.contextPosition = contextPosition or (self.position[0] + self.size[0] // 2, self.position[1] + self.height() // 2)
        self.waveLoaderPosition = waveLoaderPosition or (int(self.position[0] + self.fixSize[0] / 2 - (int(self.size[0] * self.scale) / 2)),
                                                         self.position[1] + int(self.size[1] * self.scale))
        self.contextManager = contextManager or ContextManager(self, position=self.contextPosition)

        self.isAI = isAI
        self.ollama = None
        if isAI:
            self.ollama = ollama or Ollama(*ollamaArgs, **(ollamaKwargs or {}))

        self.realtimeRecording = RealtimeRecording(*recordingArgs, **(recordingKwargs or {}))
        self.waveLoader = None
        kwargs = {
            "parent": self,
            "recording": self.realtimeRecording,
            "waveColor": "blue",
            "width": int(self.size[0] * self.scale),
            "height": int(self.size[1] * self.scale) // 5,
            "fps": self.fps,
            "position": self.waveLoaderPosition
        }
        kwargs.update(waveLoaderKwargs or {})
        self.isRecording = isRecording
        self.waveLoader = WaveLoader(**kwargs)

        self.config = {
            "roleName": self.roleName,
            "modelName": self.modelName,
            "isLookingAt": self.isLookingAt,
            "isAutoBlink": self.model.isAutoBlink,
            "isAutoBreath": self.model.isAutoBreath,
            "isLog": self.model.isLog,
            "isAI": self.isAI,
            "isRecording": self.isRecording,
            "ollamaArgs": ollamaArgs,
            "ollamaKwargs": ollamaKwargs,
            "recordingArgs": recordingArgs,
            "recordingKwargs": recordingKwargs,
            "waveLoaderKwargs": waveLoaderKwargs,
            "trayArgs": trayArgs,
            "trayKwargs": trayKwargs or {"icon": iconFileName, "tooltip": title},
            "idleFrequency": self.idleFrequency,
            "fps": self.fps,
            "size": self.size,
            "scale": self.scale,
            "title": self.title,
            "iconFileName": iconFileName,
            "position": self.position,
            "contextPosition": self.contextPosition,
            "waveLoaderPosition": self.waveLoaderPosition
        }

        self.initTrayActions()

        if fromConfigureFile:
            logger.info(f"Loading {self.roleName} from configure file")

    def isInL2DArea(self, click_x, click_y):
        return gl.glReadPixels(click_x, self.height() - click_y, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)[3] > 0

    def initTrayActions(self):
        def showOrHide():
            if self.isVisible():
                self.tray.setNewActionName("隐藏桌宠", "显示桌宠")
                self.hide()
            else:
                self.tray.setNewActionName("显示桌宠", "隐藏桌宠")
                self.show()

        self.tray.addTrayAction("隐藏桌宠", showOrHide)

        def showOrHideWave():
            if self.waveLoader.isVisible():
                self.tray.setNewActionName("禁用系统监听", "启用系统监听(会大量消耗系统资源)")
                self.waveLoader.stopRecording()
                self.waveLoader.hide()
            else:
                self.tray.setNewActionName("启用系统监听(会大量消耗系统资源)", "禁用系统监听")
                self.waveLoader.startRecording()
                self.waveLoader.show()

        self.tray.addTrayAction("禁用系统监听", showOrHideWave)
        self.tray.addTrayAction("退出", lambda: self.exit())

    def initializeGL(self):
        logger.info(f"Initializing {self.roleName} with model {self.modelName}")
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
            self.position = (int(self.x() + x - self.clickX), int(self.y() + y - self.clickY))
            self.move(*self.position)
            self.contextPosition = (int(self.x() + x - self.clickX) + self.width() // 2 - self.contextManager.width() // 2,
                                    int(self.y() + y - self.clickY) + self.height() // 2 - self.contextManager.height() // 2)
            self.contextManager.updatePosition(self.contextPosition)
            if self.realtimeRecording:
                self.waveLoaderPosition = int(self.waveLoader.x() + x - self.clickX), int(self.waveLoader.y() + y - self.clickY)
                self.waveLoader.move(*self.waveLoaderPosition)

            self.config["position"] = self.position
            self.config["contextPosition"] = self.contextPosition
            self.config["waveLoaderPosition"] = self.waveLoaderPosition

    def timerEvent(self, event):
        if self.isRunning:
            local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
            self.isInLA = self.isInL2DArea(local_x, local_y)

            if self.isLookingAt:
                self.model.lookAt(local_x, local_y)

            self.update()

    def exit(self):
        self.isRunning = False
        self.threadPool.close()
        try:
            if self.model:
                self.model.unload()
            if self.contextManager:
                self.contextManager.cleanUp()
            if self.waveLoader:
                self.waveLoader.cleanup()
            if self.ollama:
                self.ollama.close()
        except Exception as e:
            logger.warning(f"Error while exiting {self.roleName}: {e}")

        saveToConfigureFile(self.roleName, self.config)

        super().exit()

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

    def loadRandomMotion(self, group: str, priority: int = 1):
        logger.info(f"Loading random motion in group {group}")
        groups: list[str] = getMotionGroups(self.modelName)[group]
        if len(groups) > 0:
            self.model.startRandomMotion(group, self.idleFrequency, priority=priority)

    def loadExpression(self, expressionName: str):
        if expressionName in getAllExpression(self.modelName):
            self.model.setExpression(expressionName)
        else:
            logger.warning(f"Expression {expressionName} not found in model {self.modelName}")

    def start(self):
        logger.info(f"Starting {self.roleName} with model {self.modelName}")
        self._run()
        self.loadStartMotion()
        self.timer(self.idleFrequency, callback=self.loadIdleMotion)
        logger.success(f"{self.roleName} started successfully")

    @staticmethod
    def loadFromConfig(*args, **kwargs) -> "RoleLive2D":
        pass

    @staticmethod
    def sleep(seconds: float):
        time.sleep(seconds)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = RoleLive2D("Lafei",
                        "lafei_4",
                        size=(300, 400),
                        isLookingAt=True,
                        isAutoBlink=True,
                        isAutoBreath=True,
                        isLog=True,
                        isAI=False,
                        waveLoaderKwargs={"waveColor": "red"})
    widget.start()
    sys.exit(app.exec())


def loadRoleFromConfig(configFilename: str, defineClass: Type[RoleLive2D] = RoleLive2D) -> RoleLive2D:
    return defineClass.loadFromConfig(fromConfigureFile=True, **loadFromConfigureFile(configFilename))
