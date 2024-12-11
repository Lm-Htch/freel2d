import json
import os

from src.main import *


def getAllModels():
    res = []
    for models in os.listdir(MODEL_PATH):
        # 验证是否为模型文件夹
        if os.path.exists(os.path.join(MODEL_PATH, models, f"{models}.model3.json")):
            res.append(models)
    return res


def getAllExpression(modelName):
    expList = []
    basePath = str(os.path.join(RESOURCES_PATH, "models", modelName))
    for expFile in os.listdir(basePath):
        if expFile.endswith(".exp3.json"):
            expList.append(expFile.split(".")[0])
    if os.path.exists(os.path.join(basePath, "expressions")):
        for expFile in os.listdir(os.path.join(basePath, "expressions")):
            if expFile.endswith(".exp3.json"):
                expList.append(expFile.split(".")[0])
    return expList


def getMotionGroups(modelName) -> dict:
    """
    获取模型的动作组
    {
        "GroupName": FileCount
    }
    :param modelName:
    :return:
    """
    basePath = str(os.path.join(MODEL_PATH, modelName))
    data = json.load(open(os.path.join(basePath, f"{modelName}.model3.json"), "r", encoding="utf-8"))
    return {k: [v["File"].split(".")[0] for v in data["FileReferences"]["Motions"][k]] for k in data["FileReferences"]["Motions"]}


if __name__ == '__main__':
    # print(getAllModels())
    # print(getAllExpression("test"))
    print(getMotionGroups("lafei_4"))
