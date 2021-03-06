"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/31 20:49
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot import on_message, get_driver
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "repeater"),
    description="自动+1",
    usage="被动,无命令" + add_target(60)
)

repeater_last = ""
msg_last = {}


repeater = on_message(priority=12)
@repeater.handle()
async def _(event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        try:
            global repeater_last
            pres: set = get_driver().config.command_start
            # 只重复文字信息
            msg = event.get_plaintext()
            if not msg:
                return

            # 防止重复 CQ码+空格 信息
            if msg == " ":
                if not str(event.get_message()) == " ":
                    return

            # 只重复一个 +1 事件
            if repeater_last == msg:
                return

            # 不重复命令
            for pre in pres:
                if pre in msg:
                    return

            gid = event.group_id
            if gid in msg_last and msg == msg_last[gid]:
                msg_last.pop(gid)
                repeater_last = msg
                await repeater.finish(Message(msg))
            else:
                msg_last[gid] = msg
        except FinishedException:
            pass
        except Exception as e:
            logger.error(str(e))
