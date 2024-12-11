import json

from src.main import *

"""
来自`https://github.com/Arkueid/Live2DMotion3Repair`
"""


def recount_motion(motion: dict) -> tuple[int, int, int]:
    """
    重新计算*.motion3.json文件中curveCount, TotalSegmentCount和TotalPointCount的值
    """
    segment_count = 0
    point_count = 0
    curves = motion["Curves"]
    curve_count = len(curves)
    for curve in curves:
        segments = curve["Segments"]
        end_pos = len(segments)
        point_count += 1
        v = 2
        while v < end_pos:
            identifier = segments[v]
            if identifier == 0 or identifier == 2 or identifier == 3:
                point_count += 1
                v += 3
            elif identifier == 1:
                point_count += 3
                v += 7
            else:
                raise Exception("unknown identifier: %d" % identifier)
            segment_count += 1
    return curve_count, segment_count, point_count


def load_all_motion_path_from_model_dir(model_dir: str) -> list[str]:
    """导入模型文件夹中所有的motion3.json文件*路径*"""
    ls = list()
    for i in os.listdir(os.path.join(model_dir, "motions")):
        ls.append(str(os.path.join(model_dir, "motions", i)))
    return ls


def load_motion_from_path(path: str) -> dict:
    """通过motion3.json文件的路径导入"""
    return json.load(open(path, 'r'))


def copy_modify_from_motion(motion_path: str, save_root: str = "motions") -> None:
    """
    加载motion3.json文件, 重新计算并修改CurveCount, TotalSegmentCount和TotalPointCount的值, 并导出新的motion3.json文件
    :param save_root: 保存位置
    :param motion_path: 原文件路径
    :return:
    """
    motion = load_motion_from_path(motion_path)
    curve_count, segment_count, point_count = recount_motion(motion)
    motion["Meta"]["CurveCount"] = curve_count
    motion["Meta"]["TotalSegmentCount"] = segment_count
    motion["Meta"]["TotalPointCount"] = point_count
    save_path = str(os.path.join("\\".join(motion_path.split("\\")[0:-2]), save_root))

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(os.path.join(save_path, os.path.split(motion_path)[-1]), "w") as f:
        f.write(json.dumps(motion, indent=2, ensure_ascii=True))


def fixModel(modelName: str):
    """
    修复模型中的motion3.json文件
    :param modelName: 模型名称
    :return:
    """
    motionPathList = load_all_motion_path_from_model_dir(os.path.join(MODEL_PATH, modelName))
    for path in motionPathList:
        print("修复motion文件: ", path, sep="")
        copy_modify_from_motion(path)

    print("修复完成")
