import gc
import time
from enum import Enum
from typing import TextIO

import ollama
from PySide6.QtGui import QPainter, QMouseEvent, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QStyleOption, QStyle, QHBoxLayout, QLineEdit

from src.main.python.com.wutong.livepet.liveWidget import LiveWidget
from src.main.python.com.wutong.livepet.liveWidget.components import Component
from src.main.python.com.wutong.livepet.liveWidget.components.PetContext import PetContext
from src.main.python.com.wutong.livepet.widgets.Runnable import Runnable


class ChatRole(Enum):
    System = "system"
    User = "user"
    Assistant = "assistant"


class ChatMessage:
    def __init__(self, role: ChatRole | str, message: str, image: str = None):
        self.message = message
        self.role = role if isinstance(role, str) else role.value
        self.image = image

    def __dict__(self):
        return {"content": self.message, "role": self.role, "image": self.image}

    def __iter__(self):
        return iter(self.__dict__().items())


class PetChat(QWidget, Component):
    def __init__(self,
                 width: int,
                 height: int,
                 positionX: int,
                 positionY: int,
                 petContext: PetContext,
                 modelName: str,
                 system: str | TextIO = None,
                 widgetQss: str = "",
                 entryQss: str = "",
                 buttonQss: str = "",
                 tools: list[callable] = None,
                 **options):
        super().__init__(componentName="PetChat")
        self.modelNames = [i.model for i in list(ollama.list())[0][1]]

        self.petContext = petContext
        self.modelName = modelName

        self.liveWidget: LiveWidget | None = None

        self.system = (system or "") if isinstance(system, str) else system.read()
        self.options = options

        self.width = width
        self.height = height
        self.positionX = positionX
        self.positionY = positionY

        self.widgetQss = widgetQss or """
            background-color: #282C34; /* VS Code 默认深色背景色 */
            border-radius: 5px;
            padding: 5px;
        """

        self.entryQss = entryQss or """
            background-color: #3C3836; /* 深灰色输入框背景 */
            border: 1px solid #555; /* 浅灰色边框 */
            padding: 5px;
            color: #EEEEEE; /* 浅灰色文本 */
            text-align: left;
            QScrollBar::vertical {      /* 垂直滚动条 */
                width: 0px;             /* 宽度设为 0 */
            }
            QScrollBar::horizontal {    /* 水平滚动条 */
                height: 0px;            /* 高度设为 0 */
            }
        """

        self.buttonQss = buttonQss or """
            background-color: #4CAF50; /* 绿色按钮，可根据喜好修改 */
            color: white;
            padding: 5px;
            text-align: center;
            border: none;
            border-radius: 3px; /* 可选: 添加圆角 */
        """

        self.history: list[ChatMessage] = []
        if self.system:
            self.history.append(ChatMessage(ChatRole.System, self.system))

        self.tools = tools or []

        # UI
        self.layout = QHBoxLayout()
        self.chatEntry = QLineEdit()
        self.chatButton = QPushButton("发送")

        self.isRunnable = True

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def initUI(self):
        self.setStyleSheet(self.widgetQss)
        self.chatEntry.setStyleSheet(self.entryQss)
        self.chatButton.setStyleSheet(self.buttonQss)
        self.setGeometry(self.positionX, self.positionY, self.width, self.height)
        self.chatEntry.setFixedWidth(int(self.width * 5 / 6))
        self.chatEntry.setFixedHeight(self.height)
        self.layout.addWidget(self.chatEntry)
        self.chatButton.setFixedWidth(int(self.width / 6))
        self.chatButton.setFixedHeight(self.height)

        def run():
            def send():
                message = self.chatEntry.text()
                if message:
                    self.chat(message)
                    self.chatEntry.clear()

            self.liveWidget.threadPool.start(Runnable(send))
            self.hide()

        self.chatButton.clicked.connect(run)
        self.layout.addWidget(self.chatButton)
        self.setLayout(self.layout)
        self.setParent(self.liveWidget)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def chat(self, message: str | ChatMessage):
        self.petContext.clearText()
        self.history.append(message if isinstance(message, ChatMessage) else ChatMessage(ChatRole.User, message))
        result = ""
        resp = ollama.chat(self.modelName, self.history, options=self.options, stream=True, keep_alive=10, tools=self.tools)
        for chunk in resp:
            if chunk:
                chunk = chunk['message']['content']
                result += chunk
                self.petContext.addText(chunk)
        self.history.append(ChatMessage(ChatRole.Assistant, result))
        if not self.petContext.isShowing:
            def run():
                tmpTime = self.petContext.showTime
                while tmpTime > 0 and self.isRunnable:
                    tmpTime -= 0.01
                    time.sleep(0.01)
                self.petContext.clearText()

            self.liveWidget.threadPool.start(Runnable(run))

    def componentRunnable(self, liveWidget: LiveWidget) -> bool:
        self.liveWidget = liveWidget
        if self.modelName in self.modelNames:
            self.modelName = self.modelName
        else:
            self.liveWidget.logger.warning(f"Model {self.modelName} not found, use {self.modelNames[0]} instead.")
            self.modelName = self.modelNames[0]
        self.initUI()
        # 预加载模型
        self.liveWidget.logger.info(f"Preloading model {self.modelName}...")
        ollama.chat(self.modelName, [], options=self.options)
        self.liveWidget.logger.success(f"PetChat component initialized with model {self.modelName}.")
        return True

    def componentMove(self, event: QMouseEvent) -> None:
        self.positionX = self.liveWidget.positionX
        self.positionY = self.liveWidget.positionY + self.liveWidget.scaledSize[1]
        self.move(self.positionX, self.positionY)
        if self.isVisible():
            self.hide()

    def componentRelease(self) -> bool:
        self.isRunnable = False
        self.hide()
        self.close()
        # 卸载模型
        self.liveWidget.logger.info(f"Unloading model {self.modelName}...")
        ollama.chat(self.modelName, [], keep_alive=0)
        self.liveWidget.logger.success(f"PetChat component released with model {self.modelName}.")

        gc.collect()
        return True
