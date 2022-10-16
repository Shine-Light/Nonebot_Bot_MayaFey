"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/3 14:53
"""
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Event, MessageSegment, Message
from nonebot.rule import Rule
from nonebot import on_message, get_driver
from nonebot.plugin import PluginMetadata


from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "flash"),
    description="将捕获的闪照,通过私聊发送给根用户",
    usage="被动,无命令" + add_target(60)
)


def checker():
    async def _checker(bot: Bot, event: Event) -> bool:
        meta_msg = str(event.get_message())
        if "type=flash" in meta_msg:
            return True

    return Rule(_checker)


flash = on_message(rule=checker(), priority=12, block=False)
@flash.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    supers = get_driver().config.superusers
    if supers:
        CQ = str(event.get_message()).split(",")
        file = CQ[1].split("file=")[1]
        for su in supers:
            await bot.send_private_msg(user_id=int(su), message=Message(MessageSegment.image(file)))
