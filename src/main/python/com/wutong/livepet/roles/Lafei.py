import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.main.python.com.wutong.livepet.liveWidget.components.SystemTray import SystemTray
from src.main.python.com.wutong.livepet.liveWidget.components.WaveListener import WaveListener
from src.main.python.com.wutong.livepet.widgets.PetWidget import PetWidget


class Lafei(PetWidget):
    def __init__(self, app):
        super().__init__(app=app, petName="拉菲 - Live2D", modelName="lafei_4", width=550, height=500, scale=0.8)
        self.isLookingAt = True

    def initUI(self):
        self.addComponent(SystemTray(self.petName))
        self.addComponent(
            WaveListener(width=self.frameWidth, height=100, scale=self.frameScale, positionX=self.positionX, positionY=self.positionY + self.frameHeight - 100, waveColor="pink"))
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
            self.model.startContinuousMotions({"Mission": ["mission", 1], "MissionComplete": ["mission_complete", 2], "Main": ["main_2", 3]}, allPriority=2)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)


def start():
    pet = Lafei(QApplication(sys.argv))
    pet.start()


if __name__ == '__main__':
    start()
