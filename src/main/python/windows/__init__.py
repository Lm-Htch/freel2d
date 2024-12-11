import pyautogui


def getCenterPosition(__size: tuple[int, int]):
    screen_width = pyautogui.size().width
    screen_height = pyautogui.size().height

    center_x = screen_width // 2 - __size[0] // 2
    center_y = screen_height // 2 - __size[1] // 2
    return center_x, center_y
