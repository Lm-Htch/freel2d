from PySide6.QtWidgets import QApplication

from src.main.python.com.wutong.livepet.liveWidget.components.SystemTray import SystemTray
from src.main.python.com.wutong.livepet.widgets.PetWidget import PetWidget


class Hiyori(PetWidget):  # 继承自 PetWidget
    def __init__(self, app: QApplication):  # 构造函数 传入 app

        super().__init__(app,
                         "Hiyori",
                         "Hiyori",
                         300,
                         500,
                         None,
                         None,
                         None,
                         1.0,
                         True,
                         True,
                         True,
                         60,
                         60)
        """
                        app: 应用对象
                        petName: 桌宠名
                        modelName: 模型名（模型文件夹名字）
                        width: 显示宽度
                        height: 显示高度
                        parent: QWidget的父对象
                        positionX: 出现位置X坐标 Default: None （X居中显示）
                        positionY: 出现位置Y坐标 Default: None （Y居中显示）
                        scale: 缩放比例 Default: 1.0
                        isAutoBlink: 是否自动眨眼 Default: True
                        isAutoBreath: 是否自动呼吸 Default: True
                        isLookingAt: 是否Live2D目光鼠标跟随 Default: True
                        fps: 运行帧数 Default: 60
                        idleFrequency: 待机随机动作播放频率 Default: 60.0
                """

    def initUI(self):
        """
        初始化UI，用于加载控件等等操作
        """
        self.addComponent(SystemTray("Hiyori - Pet"))  # 添加系统托盘控件：托盘显示名称为Hiyori - Pet

        super().initUI()  # 调用父类方法初始化UI (包括窗口置顶等操作)

    def loadInit(self):
        """
        加载初始化，用于加载模型、动作、资源等等操作
        可以在这里加载模型加载后的模型动作，比如登录等等模型动作
        也可以设置随机闲置动作启动
        :return:
        """
        self.model.startRandomMotion(groupName="Idle",
                                     priority=2,
                                     interval=self.idleFrequency,
                                     startCallback=lambda group, index: print(f"Start Idle Motion: {group} - {index}"),
                                     endCallback=lambda: print(f"End Idle Motion"))  # 启动待机动作(循环执行)
        """
                                    groupName – 动作组名
                                    priority – 优先级
                                    interval – 间隔时间
                                    startCallback – 开始回调函数，参数为组号和索引: startCallback(group, index)
                                    endCallback – 结束回调函数: endCallback()
        """

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isInL2DArea(self.clickX, self.clickY):  # 判断点击是否在Live2D区域内
            self.model.startMotion(groupName="TapBody",
                                   motionName="Hiyori_m04",
                                   priority=1,
                                   startCallback=lambda group, index: print(f"Start TapBody Motion {group}, {index}"),
                                   endCallback=lambda: print("End TapBody Motion"))
        """
                                    groupName – 动作组名
                                    motionName – 动作名
                                    priority – 优先级
                                    startCallback – 动作开始回调函数，参数为组号和索引: startCallback(group, index)
                                    endCallback – 动作结束回调函数: endCallback()
        """

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)  # 调用父类方法处理鼠标移动事件，父类实现了Live2D鼠标拖动功能
