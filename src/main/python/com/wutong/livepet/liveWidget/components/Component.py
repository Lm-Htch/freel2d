from PySide6.QtGui import QMouseEvent

from src.main.python.com.wutong.livepet.liveWidget import LiveWidget


class Component:
    """
    组件基类
    用于LiveWidget的组件化开发
    组件的基类，继承这个类，实现componentRunnable函数
    """

    def __init__(self, componentName: str = __name__):
        """
        初始化组件
        :param componentName: 组件名称
        """
        self.componentName = componentName.split('.')[-1]

    def componentRunnable(self, liveWidget: LiveWidget) -> bool:
        """
        继承组件的类需要覆写这个函数，用于达到调用这个组件功能的目的
        :param liveWidget: 提供组件所需的LiveWidget对象
        :return:  是否成功调用组件功能 - True/False
        """
        ...

    def componentRelease(self) -> bool:
        """
        组件释放函数
        组件释放时需要执行的操作，如关闭线程、释放资源等
        :return:
        """
        ...

    def componentMove(self, event: QMouseEvent) -> None:
        """
        组件移动函数
        组件移动时需要执行的操作，如更新组件位置等
        :param event: 鼠标事件
        :return:
        """
        ...

    def serialize(self) -> dict:
        """
        序列化函数
        序列化组件信息，用于保存组件状态
        :return: 序列化后的字典
        """
        return self.__dict__

    def deserialize(self, data: dict) -> bool:
        """
        反序列化函数
        反序列化组件信息，用于恢复组件状态
        :param data: 反序列化的字典
        :return:  是否成功反序列化 - True/False
        """
        self.__dict__.update(data)
        return True
