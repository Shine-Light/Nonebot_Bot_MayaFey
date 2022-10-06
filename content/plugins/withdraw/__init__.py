"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/11 22:10
"""
import datetime
from typing import Any, Dict
from nonebot import require, on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, Event
from nonebot.plugin import PluginMetadata
from utils.other import add_target, translate
scheduler = require("nonebot_plugin_apscheduler").scheduler
from nonebot_plugin_apscheduler import scheduler


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "withdraw"),
    description="定时撤回",
    usage="被动,无命令" + add_target(60)
)


# 撤回信息
async def withdraw_message(bot: Bot, message_id: int):
    await bot.delete_msg(message_id=message_id)


# 保存需要撤回的信息
async def save_msg_id(bot: Bot, e: Exception, api: str,  data: Dict[str, Any], result: Any) -> None:
    # 处理群聊消息
    try:
        if api == "send_msg" or api == "send_group_msg":
            message_type = data["message_type"]
            if message_type == "group":
                pass
            else:
                return
        else:
            return
    except KeyError:
        return

    message_ = data["message"]
    message = ""
    # 组合信息判断(图片+文字)
    if type(message_) == Message and len(message_) > 1:
        for m in message_:
            # 识别是否为需要撤回的信息: 该消息将于 {time} s后撤回
            try:
                if "s后撤回" not in m.data["text"]:
                    continue
            except (KeyError, AttributeError):
                continue
            message = m
            break
    elif type(message_) == MessageSegment or len(message_) == 1:
        # 识别是否为需要撤回的信息: 该消息将于 {time} s后撤回
        try:
            if type(message_) == Message:
                message = message_[0]
            if "s后撤回" not in message.data["text"]:
                return
        except (KeyError, AttributeError):
            return

    if not message:
        return

    # 时间处理
    mid: int = result["message_id"]
    second: int = int(message.data["text"].split("消息将于")[1].split("s")[0])
    now = datetime.datetime.now()
    withdraw_time = now + datetime.timedelta(seconds=second)
    scheduler.add_job(withdraw_message, "date", run_date=withdraw_time, args=[bot, mid], coalesce=True)


# 在bot调用API后执行函数
Bot._called_api_hook.add(save_msg_id)


# 测试用
# test = on_command("测试", priority=8)
# @test.handle()
# async def _(bot: Bot, event: Event):
#     await bot.send(event=event, message=add_target(10))
