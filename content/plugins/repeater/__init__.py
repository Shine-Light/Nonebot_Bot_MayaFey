"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/31 20:49
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot import on_message
from nonebot.exception import FinishedException
from nonebot.log import logger


msg_last = {}

repeater = on_message(priority=12)
@repeater.handle()
async def _(event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        try:
            msg = event.get_message()
            gid = event.group_id
            if gid in msg_last and msg == msg_last[gid]:
                await repeater.finish(Message(msg))
            else:
                msg_last[gid] = msg
        except FinishedException:
            pass
        except Exception as e:
            logger.error(str(e))
