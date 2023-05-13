"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 21:48
"""
import ujson as json
import time

from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from utils.path import *
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from utils import json_tools, other

fts = "%Y-%m"


# 插件调用统计
@run_preprocessor
async def total(matcher: Matcher, event: GroupMessageEvent):
    module_names = matcher.module_name.split('.')
    plugin_name = matcher.plugin_name
    month = time.strftime(fts, time.localtime())
    msg = event.get_plaintext()
    if "init" in module_names or "utils" in module_names:
        return
    if "启用" in msg or "停用" in msg:
        return
    unable: list = open(total_unable, 'r', encoding='utf-8').read().split(",")
    if plugin_name in unable:
        return
    gid = str(event.group_id)
    total_path = total_base / month / f"{gid}.json"
    if not Path.exists(total_base / month):
        await other.mk("dir", total_base / month, content=None)
    if not Path.exists(total_path):
        await other.mk("file", total_path, 'w', content=json.dumps({}))
    js: dict = json_tools.json_load(total_path)
    if plugin_name in js:
        js.update({plugin_name: int(js[plugin_name]) + 1})
    else:
        js.update({plugin_name: 1})
    json_tools.json_write(total_path, js)
