import sys
from multiprocessing.pool import ThreadPool

from PySide6.QtGui import Qt, QPainter, QPaintEvent
from PySide6.QtWidgets import QApplication, QWidget, QStyleOption, QStyle, QLabel, QVBoxLayout


class ContextManager(QWidget):
    def __init__(self, parent=None, size: tuple[int, int] = (20, 10), scale: float = 1.0, position: tuple[int, int] = (0, 0)):
        super().__init__(parent)
        self._size = size
        self._scale = scale
        self._width = size[0] * scale
        self._height = size[1] * scale
        self._position = position
        self.fixedSize = (self._width, self._height)

        self.content = QLabel(self)
        self.layout = QVBoxLayout(self)

        self.isFinished = False

        self.move(*map(int, (self._position[0] - self._width // 2, self._position[1] - self._height // 2)))
        self.threadPool = ThreadPool(20)
        self.createEntry()

    def paintEvent(self, event: QPaintEvent) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, QPainter(self), self)
        super().paintEvent(event)

    def createEntry(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("ContextManager {background-color:rgba(0,0,0,0.5);border-radius:5px;max-width:300px;max-height:100px;}")

        self.layout.addWidget(self.content)

    def addContentByStream(self, text: str):
        self.content.setText(self.content.text() + text)

    def setContent(self, text: str):
        self.content.setText(text)

    def clearContent(self):
        self.content.setText("")

    def updatePosition(self, position: tuple[int, int]):
        self._position = position
        self.move(*map(int, (self._position[0] - self._width // 2, self._position[1] - self._height // 2)))
        # self.content.move(*map(int, (self._position[0] - self._width // 2, self._position[1] - self._height // 2)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ContextManager(size=(400, 200), position=(1920 // 2, 1080 // 2))
    widget.show()
    sys.exit(app.exec())
