import librosa
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from loguru import logger
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.main.python.patFunction.RealtimeRecording import RealtimeRecording


class WaveLoader(QWidget):
    def __init__(self, parent=None,
                 width=500,
                 height=200,
                 recording: RealtimeRecording = None,
                 position: tuple[int, int] = None,
                 fps: int = 30,
                 waveColor: tuple[int, int, int] | str = (255, 255, 255)):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet("background:transparent;")

        self.figure = Figure(facecolor=(0, 0, 0, 0))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)

        self.recording = recording or RealtimeRecording()
        self.decoder = np.float64

        self.noise_profile = None
        self.noise_update_counter = 0
        self.noise_update_interval = 30
        self.alpha = 0.9  # 平滑因子

        self.fps = fps
        self.waveColor = waveColor

        self.position = position or self.pos().toTuple()
        self.move(self.position[0], self.position[1])

    def startRecording(self):
        self.show()
        self.recording.startRecording(self.fps, self.updatePlot)
        logger.info("Start recording.")

    def stopRecording(self):
        self.recording.stopRecording()
        self.hide()
        logger.info("Stop recording.")

    def updatePlot(self, audio_data: np.ndarray):
        audio_data = audio_data.astype(self.decoder)
        try:
            if self.noise_profile is None:
                self.noise_profile = np.abs(librosa.stft(audio_data)) ** 2

            self.noise_update_counter += 1
            if self.noise_update_counter >= self.noise_update_interval:
                new_noise_profile = np.abs(librosa.stft(audio_data)) ** 2
                self.noise_profile = self.alpha * self.noise_profile + (1 - self.alpha) * new_noise_profile  # 平滑更新
                self.noise_update_counter = 0

            stft_audio = librosa.stft(audio_data)
            magnitude = np.abs(stft_audio) ** 2

            mask = (magnitude - self.noise_profile) / magnitude  # 可能需要调整
            mask = np.maximum(mask, 0.0)
            masked_stft = stft_audio * np.sqrt(mask)
            denoised_audio = librosa.istft(masked_stft).astype(self.decoder)

            self.figure.clear()

            if denoised_audio.ndim == 1:  # 单声道
                ax = self.figure.add_subplot(111)
                ax.set_axis_off()
                librosa.display.waveshow(denoised_audio, sr=self.recording.rate, ax=ax, color=self.waveColor)
            elif denoised_audio.ndim == 2:  # 多声道
                ax_left = self.figure.add_subplot(211)
                ax_right = self.figure.add_subplot(212)
                ax_left.set_axis_off()
                ax_right.set_axis_off()
                librosa.display.waveshow(denoised_audio[:, 0], sr=self.recording.rate, ax=ax_left, color=self.waveColor)
                librosa.display.waveshow(denoised_audio[:, 1], sr=self.recording.rate, ax=ax_right, color=self.waveColor)
            else:
                logger.error("Not supported audio format.")

            self.canvas.draw()
        except Exception as e:
            logger.error(f"Error: {e}")
            self.recording.stopRecording()
            self.close()

    def closeEvent(self, event):
        self.recording.stopRecording()
        event.accept()
