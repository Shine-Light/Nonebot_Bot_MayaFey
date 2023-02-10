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

from utils.other import add_target
from utils.config import manager


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="repeater",
    description="自动+1",
    usage="被动,无命令" + add_target(60),
    extra={
        "generate_type": "general",
        "permission_common": "baned",
        "unset": False,
        "total_unable": True,
        "version": "0.0.1",
        "author": "Shine_Light",
        "translate": "复读",
        "configs_general": {
          "count_max": 3  # 触发次数阈值
        }
    }
)

repeater_last = {}
msg_last = {}


def equals(msg1: Message, msg2: Message):
    """
    检查两个Message是否相等
    """
    flag = True
    if len(msg1) != len(msg2):
        return False
    for i in range(len(msg1)):
        if msg1[i].type != msg2[i].type:
            flag = False
            break
        flag = msg1[i].data == msg2[i].data
        if msg1[i].type == "image":
            flag = msg1[i].data.get("file") == msg2[i].data.get("file")
        if not flag:
            break
    return flag


repeater = on_message(priority=12, block=False)
@repeater.handle()
async def _(event: GroupMessageEvent):
    try:
        gid = event.group_id
        pres: set = get_driver().config.command_start
        count_max = manager.getPluginConfig("repeater").get_config_general("count_max")
        msg = event.get_message()
        # 空消息
        if not (msg or len(msg)):
            return

        if not msg_last.get(gid):
            msg_last.update({gid: {"msg": msg, "count": 1}})
            return

        # 不重复命令
        for pre in pres:
            if pre == msg[:len(pre)]:
                msg_last.update({gid: {"msg": msg, "count": 1}})
                return

        # 只触发一次+1
        if repeater_last.get(gid) and equals(msg, repeater_last.get(gid)):
            return

        count = msg_last.get(gid).get('count')

        if equals(msg, msg_last.get(gid).get('msg')):
            count += 1
            if count >= count_max:
                await repeater.send(msg)
                repeater_last.update({gid: msg})
        elif repeater_last.get(gid):
            repeater_last.pop(gid)
            count = 1
        else:
            count = 1

        msg_last.update({gid: {'msg': msg, 'count': count}})
    except FinishedException:
        pass
    except Exception as e:
        logger.error(e.__traceback__)
