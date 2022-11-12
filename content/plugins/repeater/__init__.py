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

repeater_last = {}
msg_last = {}


repeater = on_message(priority=12, block=False)
@repeater.handle()
async def _(event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        try:
            gid = event.group_id
            pres: set = get_driver().config.command_start

            msg = str(event.get_message())
            # 空消息
            if not msg:
                return

            if "[CQ" in msg:
                if "[CQ:face" in msg or "[CQ:at" in msg or "[CQ:image" in msg:
                    pass
                else:
                    try:
                        msg_last.pop(gid)
                        return
                    except:
                        return

            # 只重复一个 +1 事件
            try:
                if repeater_last[gid] == msg:
                    return
                if "[CQ:image" in msg and "[CQ:image" in repeater_last[gid]:
                    if repeater_last[gid].split("file=")[1].split(",")[0] == msg.split("file=")[1].split(",")[0]:
                        return
            except KeyError:
                pass

            # 不重复命令
            for pre in pres:
                if pre == msg[:len(pre)]:
                    try:
                        msg_last.pop(gid)
                        return
                    except:
                        return

            try:
                if "[CQ:image" not in msg and gid in msg_last and msg == msg_last[gid]:
                    msg_last.pop(gid)
                    repeater_last[gid] = msg
                    await repeater.finish(Message(msg))
                elif "[CQ:image" in msg and gid in msg_last and "[CQ:image" in msg_last[gid]:
                    if msg.split("file=")[1].split(",")[0] == msg_last[gid].split("file=")[1].split(",")[0]:
                        msg_last.pop(gid)
                        repeater_last[gid] = msg
                        await repeater.finish(Message(msg))
                elif repeater_last[gid] != "":
                    msg_last[gid] = msg
                    repeater_last[gid] = ""
                else:
                    msg_last[gid] = msg
            except KeyError:
                msg_last[gid] = msg

        except FinishedException:
            pass
        except Exception as e:
            logger.error(e.__traceback__)
