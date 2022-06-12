"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/31 20:49
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot import on_message, get_driver
from nonebot.exception import FinishedException
from nonebot.log import logger


msg_last = {}

repeater = on_message(priority=12)
@repeater.handle()
async def _(event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        try:
            pres: set = get_driver().config.command_start
            # 只重复文字信息
            msg = event.get_plaintext()
            if not msg:
                return

            # 防止重复 CQ码+空格 信息
            if msg == " ":
                if not str(event.get_message()) == " ":
                    return

            # 不重复命令
            for pre in pres:
                if pre in msg:
                    return

            gid = event.group_id
            if gid in msg_last and msg == msg_last[gid]:
                msg_last.pop(gid)
                await repeater.finish(Message(msg))
            else:
                msg_last[gid] = msg
        except FinishedException:
            pass
        except Exception as e:
            logger.error(str(e))
