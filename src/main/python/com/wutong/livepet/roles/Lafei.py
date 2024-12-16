from PySide6.QtCore import Qt

from src.main.python.com.wutong.livepet.liveWidget.components.PetChat import PetChat
from src.main.python.com.wutong.livepet.liveWidget.components.PetContext import PetContext
from src.main.python.com.wutong.livepet.liveWidget.components.SystemTray import SystemTray
from src.main.python.com.wutong.livepet.liveWidget.components.WaveListener import WaveListener
from src.main.python.com.wutong.livepet.widgets.PetWidget import PetWidget


class Lafei(PetWidget):
    def __init__(self, app):
        super().__init__(app=app, petName="拉菲 - Live2D", modelName="lafei_4", width=550, height=500, scale=0.6, isLookingAt=True)

        self.tray = SystemTray(self.petName)  # 添加系统托盘
        self.petContext = PetContext(width=self.scaledSize[0],
                                     height=80,
                                     positionX=self.positionX,
                                     positionY=self.positionY - 100,
                                     showTime=30,
                                     systemTray=self.tray,
                                     textColor="white",
                                     fontSize=12,
                                     backgroundColor=(255, 128, 128, 50),
                                     fontFamily="宋体")
        self.waveListener = WaveListener(width=self.frameWidth,
                                         height=100,
                                         scale=self.frameScale,
                                         positionX=self.positionX,
                                         positionY=self.positionY + self.scaledSize[1],
                                         waveColor="pink")
        self.petChat = PetChat(
            width=self.scaledSize[0],
            height=int(50 * self.frameScale),
            positionX=self.positionX,
            positionY=self.positionY + self.scaledSize[1],
            petContext=self.petContext,
            modelName="llama3.2:latest",
            system="你的名字叫做拉菲")

    def initUI(self):
        self.addComponent(self.petContext)  # 添加桌宠说话气泡
        self.addComponent(self.waveListener)  # 添加波浪动画
        self.addComponent(self.petChat)  # 添加桌宠聊天框
        self.addComponent(self.tray)  # 添加系统托盘
        super().initUI()

    def loadInit(self):
        super().loadInit()
        self.model.startMotion("Home", "home", 1)
        self.model.startRandomMotion("Main",
                                     priority=1,
                                     interval=self.idleFrequency)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isInL2DArea(self.clickX, self.clickY) and event.button() == Qt.MouseButton.LeftButton:
            # self.petContext.clearText()
            # self.petContext.showText("我是备受期待的本森级驱逐舰拉菲，在三次所罗门海战有着极为活跃的表现，战舰？那是什么？")
            if self.petChat.isVisible():
                self.petChat.hide()
            else:
                self.petChat.show()
            self.model.startContinuousMotions({"Mission": ["mission", 1], "MissionComplete": ["mission_complete", 2], "Main": ["main_2", 3]}, allPriority=2)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
