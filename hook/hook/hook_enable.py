"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/11 15:31
"""
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.exception import IgnoredException
from utils.json_tools import json_load, json_write
from utils.path import enable_config_path

# 控制变量
a = []

# 机器人启动检测
@event_preprocessor
async def enable_check(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    msg = event.get_plaintext()
    if "初始化" in msg:
        return
    if event.get_user_id == bot.self_id:
        return
    if "启用" in msg or "停用" in msg:
        return

    js = json_load(enable_config_path)
    try:
        enable = js[gid]
        if not enable:
            raise IgnoredException(f"群 {gid} 已停用机器人")
    except KeyError:
        # 默认关闭状态
        js.update({gid: False})
        json_write(enable_config_path, js)
        raise IgnoredException(f"群 {gid} 未确认是否启用机器人")
