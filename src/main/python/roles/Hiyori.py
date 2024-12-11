from src.main.python.roles.RoleLive2D import RoleLive2D


class Hiyori(RoleLive2D):
    def __init__(self):
        super().__init__("Hiyori",
                         "Hiyori",
                         waveLoaderKwargs={"waveColor": "orange"},
                         size=(300, 500),
                         scale=0.8,
                         title="Hiyori",
                         isLog=False,
                         isAI=False,
                         idleFrequency=30)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.loadMotion("TapBody", "Hiyori_m04")

    def loadIdleMotion(self):
        self.loadRandomMotion("Idle")
