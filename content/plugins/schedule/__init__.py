"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/29 13:02
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from utils.other import add_target, translate
from .tools import *

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "schedule"),
    description="自定义定时事件",
    usage="/新增|修改定时任务 {标题} 定时|间隔|日期 {时间} {内容}(可以先空着)\n"
          "/删除定时任务 {标题}\n"
          "/定时任务列表"
          "/清理过期定时任务" + add_target(60)
)


add_schedule = on_command(cmd="增加定时消息", aliases={"新增定时信息", "新增定时消息", "增加定时信息", "添加定时信息", "添加定时消息", "添加定时任务", "新增定时任务"}, priority=8)
@add_schedule.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    raw_msg = str(event.get_message())
    gid = str(event.group_id)
    check = await raw_msg_checker(raw_msg, gid)
    if check["state"] == "error":
        await add_schedule.finish(check["error"])

    data = check["data"]

    title = data["title"]
    mode = data["mode"]
    time = data["time"]
    content = data["content"]

    if await title_is_exists(gid, title):
        await add_schedule.finish("这个标题已经存在了呢")

    if content:
        matcher.set_arg(key="content", message=Message(content))

    state["src_js"] = {
        "title": title,
        "mode": mode,
        "time": time
    }


@add_schedule.got("content", prompt="请输入信息内容")
async def _(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    content = str(matcher.get_arg("content"))
    src_js = state["src_js"]
    gid = str(event.group_id)
    if not content.strip():
        await add_schedule.finish("信息内容不可为空")
    src_js.update({"content": content})
    await save(src_js, gid)
    await add_job(gid, src_js["title"])
    await add_schedule.send("添加成功")


delete_schedule = on_command(cmd="删除定时消息", aliases={"删除定时消息", "删除定时任务"}, priority=8)
@delete_schedule.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    title = args.extract_plain_text().strip()
    if not title:
        await delete_schedule.send("标题不能为空哦")
        return
    if not title_is_exists(gid, title):
        await delete_schedule.send("是不是输错了呢?找不到这个标题耶")
    await delete_job(gid, title)
    await delete_schedule.send("删除成功")


modify_schedule = on_command(cmd="修改定时消息", aliases={"修改定时消息", "修改定时任务"}, priority=8)
@modify_schedule.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    raw_msg = str(event.get_message())
    gid = str(event.group_id)
    check = await raw_msg_checker(raw_msg, gid)

    if check["state"] == "error":
        await modify_schedule.finish(check["error"])

    data = check["data"]

    title = data["title"]
    mode = data["mode"]
    time = data["time"]
    content = data["content"]

    if not await title_is_exists(gid, title):
        await modify_schedule.finish("是不是输错了呢?找不到这个标题耶")

    if content:
        matcher.set_arg(key="content", message=Message(content))

    state["src_js"] = {
        "title": title,
        "mode": mode,
        "time": time
    }


@modify_schedule.got("content", prompt="请输入信息内容")
async def _(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    content = str(matcher.get_arg("content"))
    src_js = state["src_js"]
    gid = str(event.group_id)
    if not content.strip():
        await modify_schedule.finish("信息内容不可为空")
    src_js.update({"content": content})
    await save(src_js, gid)
    await modify_job(gid, src_js["title"])
    await modify_schedule.send("修改成功")


list_of_schedule = on_command(cmd="定时任务列表", aliases={"定时信息列表", "定时消息列表"}, priority=8)
@list_of_schedule.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    try:
        schedule_list = await get_schedule_list(gid)
    except:
        await schedule_init(gid)
        schedule_list = await get_schedule_list(gid)

    if not schedule_list:
        await list_of_schedule.finish("还没有添加过定时任务呢")

    msg = await get_schedule_plaintext(schedule_list)
    await list_of_schedule.send(msg)


clean = on_command(cmd="清理过期定时信息", aliases={"清理过期定时消息", "清理过期定时任务"}, priority=8)
@clean.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await clean_out_job()
    await clean.send("清理成功")


@scheduler.scheduled_job(trigger="cron", hour=0)
async def _():
    await clean_out_job()
    logger.info("自动清理过期定时任务")
