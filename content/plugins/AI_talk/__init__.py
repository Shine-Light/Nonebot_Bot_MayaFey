"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/16 12:35
"""
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, \
    Message, MessageSegment, PrivateMessageEvent
from nonebot.rule import to_me, command
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


# 群聊版本
AI_talk = on_message(rule=to_me(), priority=12)
@AI_talk.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 命令不处理
    if command(event.get_plaintext()):
        return
    msg = event.get_plaintext().strip()
    uid = str(event.get_user_id())
    gid = str(event.group_id)
    if msg == "" or api_type == "":
        return
    nickname = (await bot.get_group_member_info(group_id=int(gid),
                                               user_id=int(uid),
                                               no_cache=True))["nickname"]
    api_url = get_api_url(msg, uid, gid, nickname)
    if not api_url:
        logger.warning("AI聊天未生效,未配置AI聊天")
        return
    data = request_url(api_url)
    parsed = parse_res(data)
    msgs = []
    # 图灵接口 (未测试,没钱买接口)
    if parsed["type"] == "turing":
        results: list = parsed["values"]
        for result in results:
            result_type = result["resultType"]
            result_values = result["values"]
            if result_type in ["text", "url"]:
                try:
                    msgs.append(MessageSegment.text(result_values["text"]))
                except:
                    msgs.append(MessageSegment.text(result_values["url"]))
            elif result_type == "video":
                msgs.append(MessageSegment.video(result_values["video"]))
            elif result_type == "image":
                msgs.append(MessageSegment.image(result_values["image"]))
            elif result_type == "news":
                msgs.append(MessageSegment.image(result_values["image"]))
                msgs.append(MessageSegment.image(result_values["text"]))
    # 常规接口
    elif parsed["type"] == "text":
        msgs.append(MessageSegment.text(parsed["values"]))
    elif parsed["type"] == "image":
        msgs.append(MessageSegment.image(parsed["values"]))
    # 无参数示例,写不了
    elif parsed["type"] == "view":
        pass

    await AI_talk.send(Message(msgs))


# 私聊版本
AI_talk_private = on_message(priority=12)
@AI_talk_private.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    # 命令不处理
    if command(event.get_plaintext()):
        return
    msg = event.get_plaintext().strip()
    uid = str(event.get_user_id())
    if msg == "" or api_type == "":
        return
    nickname = (await bot.get_stranger_info(user_id=int(uid), no_cache=True))["nickname"]
    api_url = get_api_url(msg, uid, nickname)
    if not api_url:
        logger.warning("AI聊天未生效,未配置AI聊天")
        return
    data = request_url(api_url)
    parsed = parse_res(data)
    msgs = []
    # 图灵接口 (未测试,没钱买接口)
    if parsed["type"] == "turing":
        results: list = parsed["values"]
        for result in results:
            result_type = result["resultType"]
            result_values = result["values"]
            if result_type in ["text", "url"]:
                try:
                    msgs.append(MessageSegment.text(result_values["text"]))
                except:
                    msgs.append(MessageSegment.text(result_values["url"]))
            elif result_type == "video":
                msgs.append(MessageSegment.video(result_values["video"]))
            elif result_type == "image":
                msgs.append(MessageSegment.image(result_values["image"]))
            elif result_type == "news":
                msgs.append(MessageSegment.image(result_values["image"]))
                msgs.append(MessageSegment.image(result_values["text"]))
    # 常规接口
    elif parsed["type"] == "text":
        msgs.append(MessageSegment.text(parsed["values"]))
    elif parsed["type"] == "image":
        msgs.append(MessageSegment.image(parsed["values"]))
    # 无参数示例,写不了
    elif parsed["type"] == "view":
        pass

    await AI_talk_private.send(Message(msgs))
