"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 20:11
"""
import os

from ..utils.path import *
from ..utils.other import mk


async def init():
    if not os.path.exists(ttf_name):
        await mk("file", ttf_name, "wb", url="https://public-cdn-shanghai.oss-cn-shanghai.aliyuncs.com/nonebot/msyhblod.ttf",
                 dec="资源字体")


def format_path(path: Path) -> str:
    path = str(path).replace("\\", "/")
    return path
