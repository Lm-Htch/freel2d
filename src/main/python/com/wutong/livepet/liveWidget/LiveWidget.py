import gc
import threading

import pyautogui
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication
from loguru import logger

from src.main.python.com.wutong.livepet.liveWidget.components.Component import Component
from src.main.python.com.wutong.livepet.onInput.MouseInput import MouseInput


class LiveWidget(QOpenGLWidget):
    """
    liveWidget class
    用于显示Live2D模型等窗口的父类窗口，是所有窗口的基类
    """

    def __init__(self,
                 app: QApplication,
                 frameTitle: str = None,
                 frameWidth: int = None,
                 frameHeight: int = None,
                 positionX: int = None,
                 positionY: int = None,
                 parent=None,
                 frameScale: float = 1.0,
                 frameFps: int = 30):
        """
        初始化LiveWidget
        :param app: 应用对象
        :param frameTitle: 窗口标题
        :param frameWidth: 窗口宽度
        :param frameHeight: 窗口高度
        :param positionX:  窗口位置（左上角）X
        :param positionY:  窗口位置（左上角）Y
        :param frameScale: 窗口缩放比例
        :param frameFps: 窗口刷新率
        :return: None
        """
        super().__init__(parent=parent)

        self.app = app  # 应用对象
        """应用对象"""

        self.frameTitle = frameTitle or "liveWidget"  # 窗口标题
        """窗口标题"""
        self.frameWidth = frameWidth or 800  # 窗口宽度（未缩放）
        """未缩放窗口宽度"""
        self.frameHeight = frameHeight or 600  # 窗口高度（未缩放）
        """未缩放窗口高度"""
        self.positionX = positionX or self.getCenterPosition()[0]  # 窗口位置X
        """窗口位置X (左上角)"""
        self.positionY = positionY or self.getCenterPosition()[1]  # 窗口位置Y
        """窗口位置Y (左上角)"""

        self.frameScale = frameScale  # 窗口缩放比例
        """窗口缩放比例"""
        self.frameFps = frameFps  # 窗口刷新率
        """窗口刷新率"""

        self.clickX = -1
        """点击的x坐标"""
        self.clickY = -1
        """点击的y坐标"""

        self.fixedSize = False  # 是否固定窗口大小
        """是否固定窗口大小"""
        self.scaledSize = tuple(map(lambda x: int(x * self.frameScale), (self.frameWidth, self.frameHeight)))  # 缩放后的窗口大小
        """缩放后的窗口大小"""

        self.threadPool = QThreadPool.globalInstance()  # 线程池
        """线程池"""
        self.threadPool.setParent(self)  # 设置线程池的父对象为当前窗口

        self.logger = logger  # 日志对象
        """日志对象"""

        self.__components: list[Component] = []  # 组件列表
        """组件列表"""

        self.setGeometry(self.positionX, self.positionY, self.scaledSize[0], self.scaledSize[1])  # 设置窗口位置和大小

        self.mouseInput = MouseInput(self.logger, self.threadPool)

    def frameless(self):
        """
        无边框窗口
        :return: None
        """
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

    def topWindow(self):
        """
        置顶窗口
        :return: None
        """
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    def notToolWindow(self):
        """
        非工具窗口
        :return: None
        """
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)

    def transparentWindow(self):
        """
        透明窗口
        :return: None
        """
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def addComponent(self, component: Component):
        """
        添加组件
        :param component: 组件对象
        :return: None
        """
        self.__components.append(component)

    def addComponents(self, *components: Component):
        """
        添加组件列表
        :param components: 组件列表
        :return: None
        """
        self.__components.extend(components)

    def removeComponent(self, component: Component):
        """
        移除组件
        :param component: 组件对象
        :return: None
        """
        self.__components.remove(component)

    def getComponent(self, index: int) -> Component:
        """
        获取组件列表
        :param index: 索引
        :return: 组件列表
        """
        return self.__components[index]

    def loadComponents(self):
        """
        加载组件
        :return: None
        """
        for component in self.__components:
            self.logger.info(f"load component {component.componentName}")
            try:
                if not component.componentRunnable(self):
                    self.logger.error(f"load component {component.componentName} failed")
                    continue
                else:
                    self.logger.success(f"load component {component.componentName} successfully")
            except Exception as e:
                self.logger.exception(f"load component {component.componentName} failed, {e}", exc_info=True)
        self.logger.success("load all components successfully")

    def loadInit(self):
        """
        加载初始化
        在模型加载以后可以实现的初始化功能
        :return:
        """
        pass

    def setMaxThreadCount(self, count):
        """
        设置最大线程数
        :param count: 最大线程数
        :return: None
        """
        self.threadPool.setMaxThreadCount(count)

    def initUI(self):
        """
        初始化UI
        :return: None
        """
        ...

    def show(self):
        """
        显示窗口
        :return: None
        """
        for component in self.__components:
            self.logger.info(f"show component {component.componentName}")
            component.componentShow()
        super().show()

    @staticmethod
    def getScreenSize() -> tuple[int, int]:
        """
        获取屏幕大小
        :return: 屏幕大小元组(width, height)
        """
        return pyautogui.size().width, pyautogui.size().height

    def getCenterPosition(self) -> tuple[int, int]:
        """
        获取窗口中心位置
        :return: 窗口中心位置元组(x, y)
        """
        screenWidth, screenHeight = self.getScreenSize()
        return screenWidth // 2 - self.frameWidth // 2, screenHeight // 2 - self.frameHeight // 2

    def paintGL(self):
        pass

    def initializeGL(self):
        self.logger.info("liveWidget initializeGL")
        self.makeCurrent()
        pass

    def resizeGL(self, w, h):
        pass

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        更新点击坐标
        :param event:
        :return:
        """
        self.clickX, self.clickY = event.scenePosition().x(), event.scenePosition().y()
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        for component in self.__components:
            component.componentMove(event)

    def timerEvent(self, event):
        pass

    def wheelEvent(self, event):
        pass

    def keyPressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        pass

    def start(self):
        self.initUI()
        self.show()
        self.loadInit()
        self.update()
        self.loadComponents()
        self.update()
        self.mouseInput.startAll()
        self.logger.success("liveWidget started successfully")
        self.app.exec()  # 进入消息循环

    def hide(self):
        for component in self.__components:
            self.logger.info(f"hide component {component.componentName}")
            component.componentHide()
            self.logger.success(f"hide component {component.componentName} successfully")
        super().hide()

    def closeEvent(self, event):
        self.hide()

        for component in self.__components:
            self.logger.info(f"release component {component.componentName}")
            if component.componentRelease():
                self.logger.success(f"release component {component.componentName} successfully")
            else:
                self.logger.error(f"release component {component.componentName} failed")

        def cleanup():
            self.threadPool.releaseThread()  # 在另一个线程中释放线程池
            self.logger.success("liveWidget threadPool released")
            self.threadPool.clear()
            self.logger.success("liveWidget threadPool cleared")
            self.app.exit()  # 确保在所有清理工作完成后再退出应用
            self.logger.success("liveWidget closeEvent successfully")

        threading.Thread(target=cleanup).start()  # 在单独的线程中执行清理操作
        gc.collect()
        self.logger.success("liveWidget closed")
        event.accept()  # 接受关闭事件
