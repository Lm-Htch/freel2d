# Freel2d

* 使用 [live2d-py](https://github.com/Arkueid/live2d-py) 和 pyside6 编写 Live2D 项目
* 该项目中所使用的模型均为学习和交流使用，不存在商业用途。

## 平台支持

* Windows Python 3.12 或 Python 其他版本，在将[live2d-py](https://github.com/Arkueid/live2d-py) 自行编译以后使用

## 使用方法

* 创建虚拟环境
    * ```powershell
      python -m venv .venv
      ```
  其中 .venv 为虚拟环境的路径位置
    * 进入虚拟环境
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
  python main.py
  ```

## 拓展模型

* ```python
  from src.main.python.roles.RoleLive2D import RoleLive2D
  
  class MyModel(RoleLive2D):
    def __init__(self):
        """
        还有一些参数设置将在之后的文档中逐步添加描述
        """
        super().__init__("角色名",
                         "模型名",  # 注意：模型名必须符合模型文件所在文件夹名和模型对应文件model3.json文件名相同，此问题将在之后版本改进
                         isLog=False,  # 是否需要live2d-py输出日志
                         size=(500, 550),  # 根据自己的模型大小，自行设置
                         scale=0.7,  # 模型缩放
                         waveLoaderKwargs={"waveColor": "pink"},  # 如果开启了实时同步监听，则可以使用该设置，设置波形图颜色
                         fps=120)  # 整体帧数

    def loadStartMotion(self):  # 此方法将在模型显示加载时加载，具体实现方法可以自定义
        # 以下函数加载一个动画，其中参数为：{groupName, motionName, priority}
        # 其中motionName为文件名，去掉了motion.json后缀
        self.loadMotion("Home", "home", 2)  
        

    def loadIdleMotion(self):
        # 以下函数会在程序运行时，通过设置的idleFrequency来循环执行指定动作组里的随机动作执行
        self.loadRandomMotion("Main")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.loadMotion("Touch", "touch_special")  # 同理，加载动画
  ```

## 实现效果

![img.png](docs/main.png)

## 注：

* 本项目不做为包发布，项目基于[live2d-py](https://github.com/Arkueid/live2d-py) 实现
* 如若出现模型加载问题，请查阅 [模型修复](https://github.com/Arkueid/Live2DMotion3Repair) 或 使用项目内的 `src.main.python.modelsmotionFix.fixModel("模型名")`进行修复
