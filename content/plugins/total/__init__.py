"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 22:07
"""
import ujson as json
import time

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from utils import json_tools, other
from utils.path import *

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "total"),
    description="插件调用统计",
    usage="/插件统计 (超级用户)" + add_target(60)
)
fts = "%Y-%m"

total = on_command(cmd="插件统计", aliases={"统计", "total"}, priority=6)
@total.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    month = time.strftime(fts, time.localtime())
    unable: list = open(total_unable, 'r', encoding='utf-8').read().split(",")
    total_path = total_base / month / f"{event.group_id}.json"
    if not Path.exists(total_base / month):
        await other.mk("dir", total_base / month, content=None)
    if not Path.exists(total_path):
        await other.mk("file", total_path, 'w', content=json.dumps({}))
    js: dict = json_tools.json_load(total_path)
    message = '插件调用统计:\n'
    for plugin in js:
        if (plugin not in unable) and plugin != "test":
            message += f"{translate('e2c', plugin)}:{js[plugin]}\n"
    await total.send(message)
