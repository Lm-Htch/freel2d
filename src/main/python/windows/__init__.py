import json
import os

import pyautogui

from src.main import CONFIG_PATH


def getCenterPosition(__size: tuple[int, int]):
    screen_width = pyautogui.size().width
    screen_height = pyautogui.size().height

    center_x = screen_width // 2 - __size[0] // 2
    center_y = screen_height // 2 - __size[1] // 2
    return center_x, center_y


def saveToConfigureFile(configFile: str, configData: dict):
    with open(os.path.join(CONFIG_PATH, configFile + ".json"), "w") as f:
        f.write(json.dumps(configData, indent=4, sort_keys=True))
    return True


def loadFromConfigureFile(configFile: str) -> dict:
    with open(os.path.join(CONFIG_PATH, configFile), "r") as f:
        return json.load(f)
