"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/1/14 12:57
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from utils.json_tools import json_load
from utils.path import enable_config_path
from utils.config import manager

__plugin_meta__ = PluginMetadata(
    name="sending",
    description="控制机器人发送群聊信息,私聊插件",
    usage="/发送 {群号}(用all表示所有开启机器人的群)"
          "/显示发送者"
          "/隐藏发送者",
    extra={
        "generate_type": "general",
        "author": "Shine_Light",
        "configs_general": {
            "controller": True
        }
    }
)


sending = on_command(cmd="发送", aliases={"发送信息", "发送群聊信息"}, priority=8, permission=SUPERUSER)
@sending.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("gid", args)


@sending.got(key="gid", prompt="发送到那个群呢(用all表示所有开启机器人的群)")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    gid = matcher.get_arg("gid").extract_plain_text().strip()
    if gid != "all":
        if not json_load(enable_config_path).get(gid):
            await sending.finish("该群聊未开启机器人,无法发送")


@sending.got(key="msg", prompt="发送些什么呢")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    gid = matcher.get_arg("gid").extract_plain_text().strip()
    config = manager.getPluginConfig("sending")
    msg = str(event.original_message).replace("&#91;", "[").replace("&#93;", "]")
    if config.get_config_general("controller"):
        msg = f"[{event.sender.nickname}] " + msg
    if gid == "all":
        group = json_load(enable_config_path)
        for gid in group:
            if group[gid]:
                await bot.send_group_msg(group_id=int(gid), message=Message(msg))
    else:
        await bot.send_group_msg(group_id=int(gid), message=Message(msg))

    await sending.send("发送成功")


sender_display = on_command(cmd="显示发送者", priority=8, permission=SUPERUSER)
@sender_display.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    config = manager.getPluginConfig("sending")
    config.set_config_general("controller", True)
    await sender_display.send("修改成功")


sender_hidden = on_command(cmd="隐藏发送者", priority=8, permission=SUPERUSER)
@sender_hidden.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    config = manager.getPluginConfig("sending")
    config.set_config_general("controller", False)
    await sender_hidden.send("修改成功")
