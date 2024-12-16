import time

from PySide6.QtGui import QCursor, Qt
from PySide6.QtWidgets import QApplication

from src.main.python.com.wutong.livepet.live2d.Live2D import Live2D
from src.main.python.com.wutong.livepet.liveWidget import gl, LiveWidget
from src.main.python.com.wutong.livepet.onInput.MouseInput import MouseOperationTypes


class PetWidget(LiveWidget):
    def __init__(self,
                 app: QApplication,
                 petName: str,
                 modelName: str,
                 width: int,
                 height: int,
                 parent=None,
                 positionX: int = None,
                 positionY: int = None,
                 scale: float = 1.0,
                 isAutoBlink: bool = True,
                 isAutoBreath: bool = True,
                 isLookingAt: bool = True,
                 fps: int = 60,
                 idleFrequency: float = 60.0):
        """
        构造函数
        :param app: 应用对象
        :param petName: 桌宠名
        :param modelName: 模型名（模型文件夹名字）
        :param width: 显示宽度
        :param height: 显示高度
        :param parent: QWidget的父对象
        :param positionX: 出现位置X坐标 Default: None （X居中显示）
        :param positionY: 出现位置Y坐标 Default: None （Y居中显示）
        :param scale: 缩放比例 Default: 1.0
        :param isAutoBlink: 是否自动眨眼 Default: True
        :param isAutoBreath: 是否自动呼吸 Default: True
        :param isLookingAt: 是否Live2D目光鼠标跟随 Default: True
        :param fps: 运行帧数 Default: 60
        :param idleFrequency: 待机随机动作播放频率 Default: 60.0
        """
        super().__init__(app=app, parent=parent, frameFps=fps, frameWidth=width, frameHeight=height, frameScale=scale, frameTitle=petName, positionX=positionX, positionY=positionY)
        self.petName = petName
        self.modelName = modelName
        self.isAutoBlink = isAutoBlink
        self.isAutoBreath = isAutoBreath
        self.idleFrequency = idleFrequency

        self.isInLA = False
        """是否在Live2D区域"""
        self.clickInLA = False
        """是否点击在Live2D区域"""

        self.isLookingAt = isLookingAt
        """是否Live2D目光鼠标跟随"""
        self.isRunning = False
        """是否正在运行"""

        self.model = Live2D(self.modelName, self.threadPool, True, True)
        """Live2D模型对象"""

    def isInL2DArea(self, click_x, click_y):
        """
        判断点击的位置是否在Live2D区域
        :param click_x: 点击的x坐标
        :param click_y: 点击的y坐标
        :return: True or False
        """
        return gl.glReadPixels(click_x, self.height() - click_y, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)[3] > 0

    def initUI(self):
        """
        初始化UI
        :return: None
        """
        super().initUI()
        self.logger.info("PetWidget initUI")
        self.notToolWindow()  # 非工具窗口
        self.frameless()  # 无边框
        self.transparentWindow()  # 透明窗口
        self.topWindow()  # 置顶窗口

    def initializeGL(self):
        """
        初始化GL
        :return: None
        """
        super().initializeGL()
        self.logger.info("PetWidget initializeGL")
        self.model.initialize()

        self.startTimer(int(1000 / self.frameFps))
        self.isRunning = True

    def paintGL(self):
        """
        绘制GL
        :return:
        """
        super().paintGL()
        self.model.paint()

    def resizeGL(self, width: int, height: int):
        """
        GL窗口大小改变
        :param width: 设置的宽度
        :param height: 设置的高度
        :return:
        """
        super().resizeGL(width, height)
        self.model.resize(width, height)

    def timerEvent(self, event):
        """
        定时器事件
        :param event: 定时器事件
        :return:
        """
        super().timerEvent(event)
        if self.isRunning:
            local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
            self.isInLA = self.isInL2DArea(local_x, local_y)

            if self.isLookingAt:
                self.model.lookingAt(local_x, local_y)  # Live2D目光跟随鼠标

            self.update()

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 鼠标事件
        :return:
        """
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.isInL2DArea(x, y):
            self.clickInLA = True
            super().mousePressEvent(event)
        else:
            pass

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        :param event: 鼠标事件
        :return:
        """
        if self.isInLA:
            self.clickInLA = False
        else:
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件(只实现了拖动桌宠的功能)
        :param event: 鼠标事件
        :return:
        """
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.clickInLA:
            self.positionX, self.positionY = int(self.x() + x - self.clickX), int(self.y() + y - self.clickY)  # 更新桌宠位置
            self.move(self.positionX, self.positionY)  # 移动桌宠位置
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        """
        按键按下事件
        :param event: 按键事件
        :return:
        """
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        按键释放事件
        :param event: 按键事件
        :return:
        """
        super().keyReleaseEvent(event)

    def closeEvent(self, event):
        """
        窗口关闭事件
        :param event: 窗口事件
        :return:
        """
        self.isRunning = False  # 停止定时器
        self.model.release()  # 释放模型资源
        self.logger.success("PetWidget close")
        super().closeEvent(event)  # 调用父类的关闭事件

    def close(self):
        """
        关闭窗口
        :return:
        """
        super().close()

    def start(self):
        super().start()
