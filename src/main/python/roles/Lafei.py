from src.main.python.roles.RoleLive2D import RoleLive2D


class Lafei(RoleLive2D):
    def __init__(self):
        super().__init__("Lafei",
                         "lafei_4",
                         isLog=False,
                         size=(500, 550),
                         ollamaArgs=("llama3.2:latest",),
                         scale=0.7,
                         waveLoaderKwargs={"waveColor": "pink"},
                         fps=120)

    def loadStartMotion(self):
        self.loadMotion("Home", "home", 2)

    def loadIdleMotion(self):
        self.loadRandomMotion("Main")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.loadMotion("Touch", "touch_special")

    def mouseReleaseEvent(self, event):
        super().mousePressEvent(event)
