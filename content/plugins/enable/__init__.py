"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/11 15:44
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.permission import SUPERUSER
from utils.json_tools import json_load, json_write
from utils.path import enable_config_path


enable = on_command(cmd="启用机器人", priority=1, permission=SUPERUSER)
@enable.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        js = json_load(enable_config_path)
        js.update({str(event.group_id): True})
        json_write(enable_config_path, js)
        await enable.send("操作成功")
    except Exception as e:
        await enable.send(f"操作失败:{str(e)}")


unable = on_command(cmd="停用机器人", priority=1, permission=SUPERUSER)
@unable.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        js = json_load(enable_config_path)
        js.update({str(event.group_id): False})
        json_write(enable_config_path, js)
        await unable.send("操作成功")
    except Exception as e:
        await unable.send(f"操作失败:{str(e)}")
