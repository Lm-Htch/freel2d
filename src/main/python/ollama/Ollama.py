import json
import sys
from multiprocessing.pool import ThreadPool

import requests
from PySide6.QtWidgets import QApplication

from src.main.python.ollama import BASE_API_URL
from src.main.python.ollama.ChatMessage import ChatMessage
from src.main.python.windows.ContextManager import ContextManager


class Ollama:
    def __init__(self, modelName: str, system: str = None, options: dict = None, keepAlive: int = 5, tool: list[callable] = None):
        self.modelName = modelName
        self.system = system or ""
        self.options = options or {}

        self.keepAlive = keepAlive

        self.history: list[ChatMessage] = []
        if self.system != "":
            self.history.append(ChatMessage("system", self.system))

        self.threadPool = ThreadPool(20)
        self.tool = tool

        self.loadModel()

    def loadModel(self):
        data = {
            "model": self.modelName,
            "messages": [],
        }
        resp = requests.post(BASE_API_URL + f"chat", json=data, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        if "done_reason" in resp.json():
            if resp.json()["done_reason"] == "load":
                return True
            else:
                return False
        else:
            return False

    def unloadModel(self):
        data = {
            "model": self.modelName,
            "messages": [],
            "keep_alive": 0
        }

        resp = requests.post(BASE_API_URL + f"chat", json=data, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        if "done_reason" in resp.json():
            if resp.json()["done_reason"] == "unload":
                return True
            else:
                return False
        else:
            return False

    def chat(self, chatMessage: ChatMessage, callback: callable = None, endCallback: callable = None):
        self.history.append(chatMessage)
        data = {
            "model": self.modelName,
            "messages": [message.toDict() for message in self.history],
            "options": self.options,
            "stream": True
        }
        resp = requests.post(BASE_API_URL + f"chat", json=data, headers={"Content-Type": "application/json"}, stream=True)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                line = json.loads(line)["message"]["content"]
                print(line, end="")
                if callback:
                    self.threadPool.apply_async(callback, args=(line,))

        if endCallback:
            self.threadPool.apply_async(endCallback)

    def chatByUser(self, msg: str, callback: callable = None, endCallback: callable = None):
        self.chat(ChatMessage("user", msg), callback, endCallback)


if __name__ == "__main__":
    ollama = Ollama("llama3.2:latest")
    app = QApplication(sys.argv)
    widget = ContextManager(size=(400, 200), position=(1920 // 2, 1080 // 2))
    widget.show()
    ollama.chat(ChatMessage("user", "Hello, how are you?"), widget.addContentByStream)
    sys.exit(app.exec())
