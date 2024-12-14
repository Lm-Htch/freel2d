import os

ROOT_PATH = os.path.join(os.getcwd().split("src")[0], "")
RESOURCES_PATH = os.path.join(ROOT_PATH, "src", "resources")
MODEL_PATH = os.path.join(RESOURCES_PATH, "models")
ICON_PATH = os.path.join(RESOURCES_PATH, "icons")
CONFIG_PATH = os.path.join(RESOURCES_PATH, "config")
STYLE_PATH = os.path.join(RESOURCES_PATH, "styles")
IMAGE_PATH = os.path.join(RESOURCES_PATH, "images")
COMPONENTS_PATH = os.path.join(RESOURCES_PATH, "components")

__version__ = "0.0.1"
__author__ = "Wutong"
__package_name__ = "livepet"
