"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/11 22:10
"""
import datetime
import time
import nonebot

from typing import Any, Dict
from aiocqhttp import MessageSegment
from nonebot import require, on_command
from nonebot.adapters.onebot.v11 import Bot

ft = "%Y%m%d%H%M%S"
msgs: dict = {}


# 添加撤回标志
def add_target(time_s: int) -> str:
    return f"\n(该消息将于 {time_s} s后撤回)"


# 保存需要撤回的信息
async def save_msg_id(bot: Bot, e: Exception, api: str, data: Dict[str, Any], result: Any) -> None:
    # 处理群聊消息
    if api == "send_group_msg":
        pass
    elif api == "send_msg":
        if data["message_type"] == "group":
            pass
    else:
        return

    message: MessageSegment = data["message"][0]

    # 只处理文本
    if not isinstance(message, str) and not message.type == "text":
        return

    # 识别是否为需要撤回的信息: 该消息将于 {time} s后撤回
    if "s后撤回" not in message.data["text"]:
        return

    # 时间处理
    mid: int = result["message_id"]
    second: int = int(message.data["text"].split("消息将于")[1].split("s")[0])
    time_now = datetime.datetime.now()
    time_last = time_now + datetime.timedelta(seconds=second)
    time_result: int = int(time_last.strftime(ft))

    # 更新撤回信息字典
    msgs.update({mid: time_result})


# 在bot调用API后执行函数
Bot._called_api_hook.add(save_msg_id)


# 撤回信息
scheduler = require("nonebot_plugin_apscheduler").scheduler
timezone = "Asia/Shanghai"
@scheduler.scheduled_job("cron", second="*/1", timezone=timezone)
async def _():
    time_now = int(time.strftime(ft, time.localtime()))
    bot = nonebot.get_bot()
    deleted: list = []
    # 若当前时间等于撤回时间则进行撤回
    for msg in msgs:
        if msgs[msg] == time_now:
            await bot.delete_msg(message_id=msg)
            deleted.append(msg)
    # 已撤回信息从字典中删除
    for key in deleted:
        msgs.pop(key)

# 测试用
# test = on_command("测试", priority=8)
# @test.handle()
# async def _(bot: Bot, event: Event):
#     await bot.send(event=event, message="测试信息,该消息将于 10 s后撤回" + add_target(10))
