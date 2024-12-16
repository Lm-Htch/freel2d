import json
import os
import time

import live2d.v3.live2d as live2d
from PySide6.QtCore import QThreadPool
from live2d.v3 import LAppModel
from loguru import logger

from src import MODEL_PATH
from src.main.python.com.wutong.livepet.exception import Live2DModelNotInstalledException
from src.main.python.com.wutong.livepet.widgets.Runnable import Runnable


def findModel(modelName: str) -> str:
    """
    查找模型文件
    :param modelName: 模型文件目录名
    :return: 模型文件路径
    :raises FileNotFoundError: 模型文件不存在
    """
    if os.path.exists(os.path.join(MODEL_PATH, modelName)):
        for file in os.listdir(os.path.join(MODEL_PATH, modelName)):
            if file.endswith(".model3.json"):
                return os.path.join(MODEL_PATH, modelName, file)
    else:
        raise FileNotFoundError(f"Model {modelName} not found in {MODEL_PATH}")


class Live2D:
    def __init__(self,
                 modelName: str,
                 threadPool: QThreadPool,
                 isAutoBlink: bool = True,
                 isAutoBreath: bool = True):
        """
        Live2D 构造器
        :param modelName: 模型名，需要保证模型文件夹在 /src/main/resources/models/ 目录下
        :param threadPool: 需要传入 QThreadPool 对象，用于模型动作等等的异步处理
        :param isAutoBlink: 是否自动眨眼
        :param isAutoBreath: 是否自动呼吸
        """
        live2d.init()

        self.modelName = modelName
        """模型名"""
        self.threadPool = threadPool
        """线程池"""

        self.__model: LAppModel = live2d.LAppModel()
        """Live2D 模型对象"""

        self.isAutoBlink = isAutoBlink
        """是否自动眨眼"""
        self.isAutoBreath = isAutoBreath
        """是否自动呼吸"""

        self.logger = logger
        """日志记录器"""

    def initialize(self):
        """
        初始化 Live2D 模型
        """
        self.logger.info(f"Initializing Live2D model {self.modelName}")
        live2d.glewInit()  # 初始化 GLEW
        # live2d.setGLProperties()  # 设置 OpenGL 属性 0.2.5及以前版本

        live2d.setLogEnable(False)  # 关闭日志输出
        self.__model.LoadModelJson(findModel(self.modelName))  # 加载模型文件
        self.__model.SetAutoBlinkEnable(self.isAutoBlink)  # 设置自动眨眼
        self.__model.SetAutoBreathEnable(self.isAutoBreath)  # 设置自动呼吸

        self.logger.success(f"Live2D model {self.modelName} initialized")

    @property
    def model(self) -> LAppModel:
        """
        Live2D 模型对象
        :return: Live2D 模型对象
        """
        return self.__model

    @model.setter
    def model(self, value: LAppModel):
        """
        设置 Live2D 模型对象
        :param value: Live2D 模型对象
        """
        self.__model = value

    def resize(self, width: int, height: int):
        """
        Live2D 模型大小调整
        :param width:
        :param height:
        :return: None
        """
        if self.model:
            self.model.Resize(width, height)
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def update(self):
        """
        Live2D 模型更新
        :return: None
        """
        if self.model:
            self.model.Update()
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def draw(self):
        """
        Live2D 模型绘制
        :return: None
        """
        if self.model:
            self.model.Draw()
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def isMotionFinished(self) -> bool:
        """
        Live2D 模型动作是否播放完毕
        :return: 动作是否播放完毕
        """
        if self.model:
            return self.model.IsMotionFinished()
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def lookingAt(self, x: int, y: int):
        """
        Live2D 模型调整视线
        :param x: 目标点 x 坐标
        :param y: 目标点 y 坐标
        :return: None
        """
        if self.model:
            self.model.Drag(x, y)
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def paint(self, rgba: tuple[float, float, float, float] = (.0, .0, .0, .0)):
        """
        Live2D 模型绘制到缓冲区
        :return:
        """
        if self.model:
            live2d.clearBuffer(*rgba)
            self.model.Draw()
            self.model.Update()
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def release(self):
        """
        Live2D 模型释放
        :return: None
        """
        if self.model:
            self.model = None
            live2d.dispose()
            self.logger.success(f"Live2D model {self.modelName} released")
        else:
            logger.exception("Live2D model not initialized, cannot release")

    def touch(self, x: int, y: int, startCallback: callable = lambda group, index: None, endCallback: callable = lambda: None):
        """
        Live2D 模型触摸
        :param x: 触摸点 x 坐标
        :param y: 触摸点 y 坐标
        :param startCallback: 触摸开始回调函数，参数为组号和索引: startCallback(group, index)
        :param endCallback: 触摸结束回调函数: endCallback()
        :return: None
        """
        if self.model:
            self.model.Touch(x, y, startCallback, endCallback)
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def hitPart(self, x: int, y: int) -> str:
        """
        Live2D 模型碰撞检测
        :param x: 碰撞点 x 坐标
        :param y: 碰撞点 y 坐标
        :return: 碰撞到的部位名称
        :raises Live2DModelNotInstalledException: Live2D 模型未初始化
        """
        if self.model:
            return self.model.HitTest(x, y)
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def loadMocFile(self) -> dict:
        """
        获取 Live2D 模型的 model3.json 中的文件内容
        :return: model3.json 文件内容
        """
        if self.model:
            return json.load(fp=open(findModel(self.modelName), "r", encoding="utf-8"))
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def getMotionNameInGroup(self, groupName: str, motionName: str) -> int:
        """
        获取 Live2D 模型的某个动作组中的某个动作的索引
        :param groupName: 动作组名
        :param motionName: 动作名
        :return: 动作索引
        :raises ValueError: 动作组不存在
        :raises Live2DModelNotInstalledException: Live2D 模型未初始化
        """
        if self.model:
            groupData = self.loadMocFile()["FileReferences"]["Motions"]
            if groupName in groupData:
                for index, motion in enumerate(groupData[groupName]):
                    if motion["File"] == motionName + ".motion3.json" or motion["File"] == f"motions/{motionName}.motion3.json":
                        return index
            else:
                logger.error(f"Group {groupName} not found in model {self.modelName}")
                raise ValueError(f"Group {groupName} not found in model {self.modelName}")
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def startMotion(self, groupName: str, motionName: str, priority: int = 0, startCallback: callable = lambda group, index: None, endCallback: callable = lambda: None):
        """
        Live2D 模型动作播放
        :param groupName: 动作组名
        :param motionName: 动作名
        :param priority: 优先级
        :param startCallback: 动作开始回调函数，参数为组号和索引: startCallback(group, index)
        :param endCallback: 动作结束回调函数: endCallback()
        :return: None
        :raises Live2DModelNotInstalledException: 动作组不存在
        :raises ValueError: 动作组不存在
        """

        if self.model:
            self.threadPool.start(Runnable(self.model.StartMotion, groupName, self.getMotionNameInGroup(groupName, motionName), priority, startCallback, endCallback))
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")

    def startRandomMotion(self, groupName: str, priority: int = 0, interval: float = 60, startCallback: callable = lambda group, index: None, endCallback: callable = lambda: None):
        """
        Live2D 模型随机动作播放(循环播放)
        :param groupName: 动作组名
        :param priority: 优先级
        :param interval: 间隔时间
        :param startCallback: 开始回调函数，参数为组号和索引: startCallback(group, index)
        :param endCallback: 结束回调函数: endCallback()
        :return: None
        """
        self.logger.info(f"Starting random motion in group {groupName}")

        def run():
            nonlocal groupName, priority, interval, startCallback, endCallback
            timeSleep = interval
            while self.model and (timeSleep := timeSleep - 0.01) >= 0:
                time.sleep(0.01)
            if self.model:
                self.model.StartRandomMotion(groupName, priority, startCallback, endCallback)
                run()
            else:
                logger.info(f"Random motion in group {groupName} stopped")

        self.threadPool.start(Runnable(run))
        logger.success(f"Random motion in group {groupName} started")

    def startRandomMotionsOnce(self, groupName: str, priority: int = 0, startCallback: callable = lambda group, index: None, endCallback: callable = lambda: None):
        """
        Live2D 模型随机动作播放(仅播放一次)
        :param groupName: 动作组名
        :param priority: 优先级
        :param startCallback: 开始回调函数，参数为组号和索引: startCallback(group, index)
        :param endCallback: 结束回调函数: endCallback()
        :return: None
        """
        self.logger.info(f"Starting random motion in group {groupName}")

        def run():
            nonlocal groupName, priority, startCallback, endCallback
            if not self.model.IsMotionFinished():
                self.model.StartRandomMotion(groupName, priority, startCallback, endCallback)

        self.threadPool.start(Runnable(run))
        logger.success(f"Random motion in group {groupName} started")

    def getAllParameter(self):
        return [self.model.GetParameter(i) for i in range(self.model.GetParameterCount())]

    def startContinuousMotions(self,
                               groupForMotions: dict[str, tuple[str, int]],
                               allPriority: int = 0,
                               startCallback: callable = lambda: None,
                               endCallback: callable = lambda: None):
        """
        Live2D 模型连续动作播放
        :param groupForMotions: 动作组名和动作名的字典，并手动指定执行顺序 {groupName: (motionName, order)}
        :param allPriority: 全部动作的优先级
        :param startCallback: 全局开始回调函数: startCallback()
        :param endCallback: 全局结束回调函数: endCallback()
        :return: None
        """
        self.logger.info(f"Starting continuous motions with priority {allPriority}")

        def run():
            nonlocal groupForMotions, allPriority, startCallback, endCallback
            startCallback()
            for groupName in sorted(groupForMotions.keys(), key=lambda x: groupForMotions[x][1]):
                motionName = groupForMotions[groupName][0]
                while self.model and not self.model.IsMotionFinished():
                    time.sleep(0.01)
                    continue
                if self.model:
                    self.model.StartMotion(groupName, self.getMotionNameInGroup(groupName, motionName), allPriority)
                else:
                    logger.warning(f"Continuous motion {groupName} {motionName} stopped")
                logger.info(f"Continuous motion {groupName} {motionName} started")
            endCallback()

        if self.isMotionFinished():
            self.threadPool.start(Runnable(run))
            logger.success(f"Continuous motions started with priority {allPriority}")
        else:
            logger.warning("Cannot start continuous motions while motion is playing")

    def loadExpression(self, expressionName: str):
        """
        Live2D 模型表情播放
        :param expressionName: 表情名
        :return: None
        """
        if self.model:
            self.model.SetExpression(expressionName)
        else:
            logger.exception("Live2D model not initialized")
            raise Live2DModelNotInstalledException("Live2D model not initialized")
