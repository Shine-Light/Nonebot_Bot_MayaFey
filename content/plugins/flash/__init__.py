"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/3 14:53
"""
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Event, MessageSegment, Message
from nonebot.rule import Rule
from nonebot import on_message


def checker():
    async def _checker(bot: Bot, event: Event) -> bool:
        meta_msg = str(event.get_message())
        if "CQ:image" in meta_msg:
            CQ = meta_msg.split(",")
            type = ""
            if len(CQ) == 4:
                pass
            elif len(CQ) == 5:
                type = CQ[3].split("type=")[1]
            if type == "flash":
                return True

    return Rule(_checker)


flash = on_message(rule=checker(), priority=12)
@flash.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    CQ = str(event.get_message()).split(",")
    file = CQ[1].split("file=")[1]
    await bot.send_private_msg(user_id=3120815902, message=Message(MessageSegment.image(file)))
