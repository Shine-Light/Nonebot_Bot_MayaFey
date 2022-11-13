"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/11/8 22:19
"""
import os
import datetime

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from content.plugins.plugin_control.functions import get_state
from utils.other import add_target, translate, get_bot_name
from .tools import *

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "curfew"),
    description="在夜间禁言全员(除管理员,群主)",
    usage="/宵禁开始时间 {时间} (22:00)\n"
          "/宵禁结束时间 {时间} (7:00)\n"
          "/开启|关闭宵禁 (指开启|关闭定时禁言,不是开启|关闭禁言)" + add_target(60)
)


curfew_run_time = on_command(cmd="宵禁开始时间", priority=8, block=False)
@curfew_run_time.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args:
        matcher.set_arg("time", args)


@curfew_run_time.got(key="time", prompt="想要几点开始呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    gid = str(event.group_id)
    result = resolve(matcher.get_arg("time").extract_plain_text())
    if result['result']:
        time = result['time']
        await set_start_time(gid=gid, time={"hour": time['hour'], "minute": time['minute']})
        await modify_task(gid)
        await curfew_run_time.finish("设置成功!")
    else:
        await curfew_run_time.finish(f"你说的到底是几点啊,{get_bot_name()}完全看不懂啊喂!")


curfew_stop_time = on_command(cmd="宵禁结束时间", priority=8, block=False)
@curfew_stop_time.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args:
        matcher.set_arg("time", args)


@curfew_stop_time.got(key="time", prompt="想要几点结束呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    gid = str(event.group_id)
    result = resolve(matcher.get_arg("time").extract_plain_text())
    if result['result']:
        time = result['time']
        await set_stop_time(gid=gid, time={"hour": time['hour'], "minute": time['minute']})
        await modify_task(gid)
        await curfew_stop_time.finish("设置成功!")
    else:
        await curfew_stop_time.finish(f"你说的到底是几点啊,{get_bot_name()}完全看不懂啊喂!")


curfew_on = on_command(cmd="开启宵禁", priority=8, block=False)
@curfew_on.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    await switch(gid, True)
    await start_task(bot, gid)
    await curfew_on.finish("已开启定时宵禁")


curfew_off = on_command(cmd="关闭宵禁", priority=8, block=False)
@curfew_off.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    await switch(gid, False)
    await stop_all_task(gid)
    await curfew_off.finish("已关闭定时宵禁")


@driver.on_bot_connect
async def _(bot: Bot):
    for gid in os.listdir(curfew_path):
        try:
            if not (await get_state("curfew", gid)):
                return
            js = json_load(curfew_path / gid / "config.json")
        except:
            continue

        if js['switch']:
            await start_task(bot, gid)
