import sys

from PySide6.QtWidgets import QApplication

from src.main.python.com.wutong.livepet.roles.Hiyori import Hiyori

if __name__ == '__main__':
    pet = Hiyori(QApplication(sys.argv))  # 调用 - 传入应用程序实例
    pet.start()  # 启动程序
