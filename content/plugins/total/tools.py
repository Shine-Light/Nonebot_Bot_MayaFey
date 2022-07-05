"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/4 22:15
"""
import time


from utils.path import total_base
from utils import json_tools


fts = "%Y-%m"


async def get_count(gid: str, plugin: str):
    month = time.strftime(fts, time.localtime())
    total_path = total_base / month / f"{gid}.json"
    js: dict = json_tools.json_load(total_path)
    try:
        return js[plugin]
    except KeyError:
        return 0
