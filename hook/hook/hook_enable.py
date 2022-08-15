"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/11 15:31
"""
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.exception import IgnoredException
from utils.json_tools import json_load
from utils.path import enable_config_path

# 控制变量
a = []

# 机器人启动检测
@event_preprocessor
async def enable_check(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    if "初始化" in event.get_plaintext():
        return
    if event.get_user_id == bot.self_id:
        return
    if gid in a:
        return
    msg = event.get_plaintext()
    js = json_load(enable_config_path)
    if "启用" in msg or "停用" in msg:
        return
    try:
        enable = js[gid]
        if not enable:
            raise IgnoredException(f"群 {gid} 已停用机器人")
    except IgnoredException:
        IgnoredException(f"群 {gid} 已停用机器人")
    except Exception:
        await bot.send(event, '未找到该群配置文件,请确认本群是否开启机器人,"/启用|停用机器人"')
        a.append(gid)
        raise IgnoredException(f"群 {gid} 未确认是否启用机器人")
