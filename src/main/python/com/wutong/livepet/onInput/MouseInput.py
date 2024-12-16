from enum import Enum

from PySide6.QtCore import QThreadPool
from loguru import logger
from pynput.mouse import Listener

from src.main.python.com.wutong.livepet.widgets.Runnable import Runnable


class MouseOperationTypes(Enum):
    Click = "on_click"
    Move = "on_move"
    Scroll = "on_scroll"


class MouseInput:
    def __init__(self, log: logger, threadPool: QThreadPool = None):
        self.threadPool = threadPool or QThreadPool().globalInstance()
        self.log = log
        self.threadMouseDict: dict[str, Listener] = {}

    def start(self, bindName: str):
        self.threadPool.start(Runnable(self.threadMouseDict[bindName].start))
        self.log.success(f"Mouse input started for button {bindName} successfully")

    def startAll(self):
        for bindName in self.threadMouseDict.keys():
            self.start(bindName)
        self.log.success("Mouse input started for all buttons successfully")

    def bindMouse(self, bindName: str, key: MouseOperationTypes, func: callable):
        self.log.info(f"Bind mouse button {bindName} to {key} with function {func.__name__}")
        self.threadMouseDict[bindName] = Listener(**{key.value: func})

    def bindMoreMouse(self, bindName: str, keyToFunc: dict[MouseOperationTypes, callable]):
        addDict = {k.value: v for k, v in keyToFunc.items()}
        self.log.info(f"Bind more mouse button {bindName} to {addDict}")
        self.threadMouseDict[bindName] = Listener(**addDict)

    def close(self):
        for listener in self.threadMouseDict.values():
            listener.stop()
        self.log.info("Mouse input stopped")
        self.threadPool.releaseThread()
