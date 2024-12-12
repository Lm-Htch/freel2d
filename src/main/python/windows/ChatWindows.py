from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class ChatWindows(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 没有标题，无窗口显示
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.initUI()

    def initUI(self):
        pass

    def show(self):
        pass

    def close(self):
        pass
