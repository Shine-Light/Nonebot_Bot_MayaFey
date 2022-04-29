"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 21:48
"""
import json
import time

from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from ..utils.path import *
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from ..utils import json_tools

fts = "%Y-%m"


# 插件开关检测
@run_preprocessor
async def total(matcher: Matcher, event: GroupMessageEvent):
    module_names = matcher.module_name.split('.')
    month = time.strftime(fts, time.localtime())
    if "init" in module_names or "utils" in module_names:
        return
    unable: list = open(total_unable, 'r', encoding='utf-8').read().split(",")
    if module_names in unable:
        return
    plugin_name = matcher.plugin_name
    gid = str(event.group_id)
    total_path = total_base / month / f"{gid}.json"
    js: dict = json.loads(open(total_path, 'r', encoding='utf-8').read())
    if plugin_name in js:
        js.update({plugin_name: int(js[plugin_name]) + 1})
    else:
        js.update({plugin_name: 1})
    json_tools.json_write(total_path, js)
