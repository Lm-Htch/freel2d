# Model.py
import os.path
import random
import time
from multiprocessing.pool import ThreadPool
from threading import Thread, Timer

import live2d.v3 as live2d
from live2d.v3 import Parameter, StandardParams
from loguru import logger

from src.main import RESOURCES_PATH
from src.main.python.exception import ModelNotInitializedException
from src.main.python.models import getAllExpression


class Model:
    model: live2d.LAppModel

    def __init__(self, modelName: str, isAutoBlink: bool = True, isAutoBreath: bool = True, isLog: bool = True, lipSyncN: int = 10):
        live2d.init()
        self.modelName = modelName

        self.basePath = os.path.join(RESOURCES_PATH, f"models\\{modelName}")
        self.modelFile = f"{modelName}.model3.json"

        self.isAutoBlink = isAutoBlink
        self.isAutoBreath = isAutoBreath
        self.isLog = isLog

        self.lipSyncN = lipSyncN

        self.threadPool = ThreadPool(100)

    def initialize(self):
        live2d.glewInit()
        live2d.setGLProperties()

        self.model = live2d.LAppModel()
        if self.model:
            self.model.LoadModelJson(os.path.join(self.basePath, self.modelFile))
            self.setAutoBlinkEnable(self.isAutoBlink)
            self.setAutoBreathEnable(self.isAutoBreath)
            self.setLogEnable(self.isLog)

    def resize(self, width, height):
        if self.model:
            self.model.Resize(width, height)

    def paint(self):
        if self.model:
            live2d.clearBuffer()
            self.model.Draw()
            self.model.Update()

    def addParameterValue(self, parameterName: str | StandardParams, value: float):
        if self.model:
            self.model.AddParameterValue(parameterName, value)

    def lipSync(self, rms: float):
        if self.model:
            self.addParameterValue(StandardParams.ParamMouthOpenY, rms * self.lipSyncN)

    def touch(self, x, y, startCallback=None, endCallback=None):
        if self.model:
            self.model.Touch(x, y, startCallback, endCallback)

    def startMotion(self, group: str, index: int, priority: int = 0, onCallback=lambda g, n: None, offCallback=lambda: None):
        if self.model:
            if self.model.IsMotionFinished():
                self.model.StartMotion(group, index, priority, onCallback, offCallback)

    def startRandomMotion(self, group: str, frequency: float):
        def run():
            logger.debug("Start Random Motion")
            self.waitMotionEnd(self.model.StartRandomMotion, args=(group, 1))
            time.sleep(frequency)
            run()

        if self.model:
            self.threadPool.apply_async(run)

    def setExpression(self, name: str):
        if self.model:
            self.model.SetExpression(name)

    def expressionSwitch(self, before: str, after: str, duration: float):
        def switch():
            if self.model:
                self.setExpression(before)
                time.sleep(duration)
                self.setExpression(after)
            else:
                logger.error("Model not initialized")
                raise ModelNotInitializedException("Model not initialized")

        self.threadPool.apply_async(switch)

    def loadingExpressionForAll(self, before: str, after: str, finishCallback: str, duration: float = 3):
        def loading():
            self.setExpression(before)
            time.sleep(duration / 2)
            self.setExpression(after)
            time.sleep(duration / 2)
            self.setExpression(finishCallback)

        if self.model:
            self.threadPool.apply_async(loading)
        else:
            logger.error("Model not initialized")
            raise ModelNotInitializedException("Model not initialized")

    def randomExpression(self, expressionList: list[str], endCallExpression: str, duration: float, frequency: float):
        def run():
            while True:
                getList = random.choices(expressionList, k=2)
                self.setExpression(getList[0])
                time.sleep(duration / 2)
                self.setExpression(getList[1])
                time.sleep(duration / 2)
                self.setExpression(endCallExpression)
                time.sleep(frequency)

        if self.model and getAllExpression(self.modelName):
            self.threadPool.apply_async(run)
        else:
            logger.error("Model not initialized or no Expression found")
            raise ModelNotInitializedException("Model not initialized or no Expression found")

    def __del__(self):
        try:
            live2d.dispose()
        except Exception:
            pass

    def getAllParameter(self):
        return [self.model.GetParameter(i) for i in range(self.model.GetParameterCount())]

    def lookAt(self, x, y):
        self.model.Drag(x, y)

    def setAutoBreathEnable(self, enable: bool = True):
        self.model.SetAutoBreathEnable(enable)

    def setAutoBlinkEnable(self, enable: bool = True):
        self.model.SetAutoBlinkEnable(enable)

    @staticmethod
    def setLogEnable(enable: bool = True):
        live2d.setLogEnable(enable)

    def waitMotionEnd(self, callback=None, args: tuple = ()):
        def wait():
            while not self.model.IsMotionFinished():
                time.sleep(0.1)
            if callback:
                callback(*args)

        self.threadPool.apply_async(wait)

    def startContinuousMotions(self, groups: dict[str, list[int, int, callable, callable] | list[int, int] | list[int]], duration: float = 2.0):
        logger.debug("Start Continuous Motions")

        def run():
            for group, motions in groups.items():
                self.waitMotionEnd(self.startMotion, args=(group, *motions))
                time.sleep(duration)

        Timer(0.1, run).start()
