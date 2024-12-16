import os
import time
import wave
from datetime import datetime

import librosa
import numpy as np
import pyaudio
import sounddevice
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src import ROOT_PATH
from src.main.python.com.wutong.livepet.liveWidget import LiveWidget
from src.main.python.com.wutong.livepet.liveWidget.components import Component
from src.main.python.com.wutong.livepet.widgets.Runnable import Runnable


class SystemRecorder:
    def __init__(self,
                 liveWidget: LiveWidget,
                 inputDrivesName: str = "立体声混音",
                 channels: int = None,
                 formats: int = pyaudio.paInt32,
                 rate: int = None,
                 chunk: int = 4096,
                 isSave: bool = False,
                 savePath: str = None,
                 fileName: str = "output"):
        """
        初始化录音类
        :param inputDrivesName: 输入设备名称
        :param channels: 通道数
        :param formats: 格式
        :param rate: 采样率
        :param chunk: 缓冲区大小
        :param savePath: 保存路径
        :param fileName: 保存文件名
        """
        self.liveWidget = liveWidget
        self.inputDrivesName = inputDrivesName
        self.drives = [i for i in SystemRecorder.getAllDrives() if inputDrivesName in i["name"]]

        if not self.drives:
            self.liveWidget.logger.exception(f"Cannot find input device {inputDrivesName}")
            raise ValueError(f"Cannot find input device {inputDrivesName}")

        self.channels = channels or self.drives[0]['max_input_channels']
        self.formats = formats
        self.rate = rate or int(self.drives[0]['default_samplerate'])
        self.chunk = chunk
        self.isSave = isSave
        self.savePath = savePath or os.path.join(ROOT_PATH, "outputWave")

        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)

        self.fileName = datetime.now().strftime(f"%Y-%m-%d_%H-%M-%S_{fileName}.wav")
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.formats, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk, input_device_index=self.drives[0]['index'])
        self.threadPool: QThreadPool = liveWidget.threadPool

        self.__isRecording = True

        if self.isSave:
            self.outputWaveFile = wave.open(os.path.join(self.savePath, self.fileName), 'wb')
            self.outputWaveFile.setnchannels(self.channels)
            self.outputWaveFile.setsampwidth(self.p.get_sample_size(self.formats))
            self.outputWaveFile.setframerate(self.rate)

    def startRecording(self, fps: int = 30, callback=lambda data: None, endCallback=lambda: None):

        def run():
            try:
                while self.__isRecording:
                    audio_data = np.frombuffer(self.stream.read(self.chunk), dtype=np.int32)
                    callback(audio_data)
                    if self.isSave:
                        self.outputWaveFile.writeframes(audio_data.tobytes())
                    time.sleep(1 / fps)
            except KeyboardInterrupt:
                pass
            finally:
                endCallback()

        self.threadPool.start(Runnable(run))

    def stopRecording(self):
        self.__isRecording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.liveWidget.logger.info("Recording stopped")

    def close(self):
        if self.isSave:
            self.outputWaveFile.close()
        self.stopRecording()

    def __repr__(self):
        return "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])

    @staticmethod
    def getAllDrives():
        return [i for i in sounddevice.query_devices()]


class WaveListener(QWidget, Component):
    def __init__(self,
                 width: int,
                 height: int,
                 scale: float,
                 positionX: int,
                 positionY: int,
                 waveColor: str | tuple[float, float, float, float] = "blue"):
        super().__init__(componentName=__name__)
        self.width = int(width * scale)
        self.height = int(height * scale)
        self.positionX = positionX
        self.positionY = positionY
        self.waveColor = waveColor

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet("background:transparent;")

        self.figure = Figure(facecolor=(0, 0, 0, 0))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)

        self.isRunning = False
        self.recording: SystemRecorder | None = None
        self.decoder = np.float64

        self.noise_profile = None
        self.noise_update_counter = 0
        self.noise_update_interval = 30
        self.alpha = 0.9  # 平滑因子

        self.clickX = -1
        self.clickY = -1

    def componentRunnable(self, liveWidget: LiveWidget) -> bool:
        self.recording = SystemRecorder(liveWidget)
        self.isRunning = True
        self.setGeometry(self.positionX, self.positionY, self.width, self.height)
        self.clickX = self.recording.liveWidget.clickX
        self.clickY = self.recording.liveWidget.clickY
        # self.show()
        self.recording.startRecording(fps=liveWidget.frameFps, callback=self.updatePlot)
        return True

    def componentRelease(self) -> True:
        self.isRunning = False
        self.recording.close()
        self.hide()
        self.close()
        return True

    def componentMove(self, event: QMouseEvent) -> None:
        self.positionX = self.recording.liveWidget.positionX
        self.positionY = self.recording.liveWidget.positionY + self.recording.liveWidget.frameHeight - 100
        self.move(self.positionX, self.positionY)

    def updatePlot(self, audio_data: np.ndarray):
        if not self.isRunning:
            return
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

            try:
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
                    self.recording.liveWidget.logger.error("Not supported audio format.")
                self.canvas.draw()
            except Exception as e:
                self.recording.liveWidget.logger.error(f"Find Unknown Error: {e}")
        except Exception as e:
            self.recording.liveWidget.logger.exception(f"Error: {e}")
            self.recording.stopRecording()

    def componentHide(self):
        self.hide()

    def componentShow(self):
        self.show()
