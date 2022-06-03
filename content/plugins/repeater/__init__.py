"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/31 20:49
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on_message
from nonebot.exception import FinishedException


msg_last = {}

repeater = on_message(priority=12)
@repeater.handle()
async def _(event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        try:
            text = event.get_plaintext()
            gid = event.group_id
            if gid in msg_last and text == msg_last[gid]:
                await repeater.finish(text)
            else:
                msg_last[gid] = text
        except FinishedException:
            pass
        except Exception as e:
            await repeater.send(f"出现错误:{str(e)}")
