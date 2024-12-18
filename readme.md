# Freel2d

* 使用 [live2d-py](https://github.com/Arkueid/live2d-py) 和 pyside6 编写 Live2D 项目
* 该项目中所使用的模型均为学习和交流使用，不存在商业用途。

## 平台支持

* Windows Python 3.12
## 版本
freel2d v0.0.2

## 使用方法

* 创建虚拟环境
  ```powershell
  python -m venv .venv
  ```
  其中 .venv 为虚拟环境的路径位置
  进入虚拟环境
  ```powershell
  .venv/Scripts/activate.bat
  ```
  若.venv不是虚拟环境路径，需要自行修改

* 添加库和依赖
  ```powershell
  pip install -r requirements.txt
  ```
* 运行
  ```powershell
  pythonw main.pyw
  ```

## 拓展模型
* 以下是拓展模型 Hiyori的用法，可以在`src/main/python/com/wutong/livepet/roles/Hiyori.py`找到
```python
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

```
* 主函数调用启动拓展模型 (`src/main/python/com/wutong/livepet/liveWidget/components/Component.py`)
```python
import sys

from PySide6.QtWidgets import QApplication

from src.main.python.com.wutong.livepet.roles.Hiyori import Hiyori

if __name__ == '__main__':
    pet = Hiyori(QApplication(sys.argv))  # 调用 - 传入应用程序实例
    pet.start()  # 启动程序
```

* 若需要自行拓展组件，可以阅读源代码
```python
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

    def componentMousePress(self, event: QMouseEvent):
        """
        组件鼠标按下函数
        组件鼠标按下时需要执行的操作，如更新组件位置等
        :param event: 鼠标事件
        :return:
        """
        ...

    def componentMouseRelease(self, event: QMouseEvent):
        """
        组件鼠标释放函数
        组件鼠标释放时需要执行的操作，如更新组件位置等
        :param event: 鼠标事件
        :return:
        """
        ...
```

## 实现效果

![main.png](docs/main.png)

## 注：

* 本项目不做为包发布，项目基于[live2d-py](https://github.com/Arkueid/live2d-py) 实现
* 如若出现模型加载问题，请查阅 [模型修复](https://github.com/Arkueid/Live2DMotion3Repair) 或 使用项目内的 `src.main.python.com.wutong.livepet.tool.fixModel("模型名")`进行修复
