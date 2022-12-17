"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/16 12:35
"""
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, \
    Message, MessageSegment, PrivateMessageEvent, Event
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata

from utils.other import add_target, translate
from .tools import *


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "AI_talk"),
    description="和真宵聊天",
    usage="群聊: @我 {聊天内容}\n"
          "私聊: {聊天内容}" + add_target(60)
)


config = get_driver().config


AI_talk = on_message(rule=to_me(), priority=12, block=False)
@AI_talk.handle()
async def _(bot: Bot, event: Event):
    msg = event.get_plaintext().strip()
    # 空消息不处理
    if msg == "" or api_type == "":
        return
    # 命令不处理
    cmd_start = config.command_start
    for start in cmd_start:
        if start == event.get_plaintext()[0]:
            return
    # 群聊处理
    if isinstance(event, GroupMessageEvent):
        uid = str(event.get_user_id())
        gid = str(event.group_id)
        nickname = (await bot.get_group_member_info(group_id=int(gid),
                                                    user_id=int(uid),
                                                    no_cache=True))["nickname"]
        api_url = get_api_url(msg, uid, nickname, gid)
    # 私聊处理
    elif isinstance(event, PrivateMessageEvent):
        uid = str(event.get_user_id())
        nickname = (await bot.get_stranger_info(user_id=int(uid), no_cache=True))["nickname"]
        api_url = get_api_url(msg, uid, nickname)
    else:
        return
    # 未配置
    if not api_url:
        logger.warning("AI聊天未生效,未配置AI聊天")
        return

    data = request_url(api_url)
    parsed = parse_res(data)
    if not parsed:
        return
    msgs = []
    # 常规接口
    for value in parsed["values"]:
        content = value["value"]
        if value["type"] == "text":
            msgs.append(MessageSegment.text(content))
        elif value["type"] == "image":
            msgs.append(MessageSegment.image(content))
        elif value["type"] == "record":
            msgs.append(MessageSegment.record(content))
        elif value["type"] == "docs":
            msgs.append(MessageSegment.text("文档地址:" + content))
        # 无参数示例,写不了
        elif value["type"] == "view":
            pass

    await AI_talk.send(Message(msgs))
