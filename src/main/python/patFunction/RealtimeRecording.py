import os
import time
import wave
from datetime import datetime
from multiprocessing.pool import ThreadPool

import numpy as np
import pyaudio
import sounddevice
from loguru import logger

from src.main import ROOT_PATH


class RealtimeRecording:
    def __init__(self,
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
        self.inputDrivesName = inputDrivesName
        self.drives = [i for i in RealtimeRecording.getAllDrives() if inputDrivesName in i["name"]]

        if not self.drives:
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
        self.threadPool = ThreadPool(10)

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

        self.threadPool.apply_async(run)

    def stopRecording(self):
        self.__isRecording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        logger.info("Recording stopped")

    def close(self):
        if self.isSave:
            self.outputWaveFile.close()
        self.stopRecording()

    def __repr__(self):
        return "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])

    @staticmethod
    def getAllDrives():
        return [i for i in sounddevice.query_devices()]
