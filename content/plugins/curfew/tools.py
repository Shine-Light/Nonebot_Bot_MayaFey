"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/11/8 22:20
"""
import datetime

import apscheduler.jobstores.base
from nonebot import require, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message

from utils.path import curfew_path
from utils.json_tools import json_write, json_load
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


driver = get_driver()
format_str = "%H:%M"
ban_all_task_id = "curfew_ban_all_%s"
unban_all_task_id = "curfew_unban_all_%s"


async def switch(gid: str, enable: bool):
    """
    @param enable: 是否开启
    @param gid: 群号
    """
    js = json_load(curfew_path / gid / "config.json")
    js['switch'] = enable
    json_write(curfew_path / gid / "config.json", js)


async def set_start_time(gid: str, time: dict):
    """
    @param time: 时间
    @param gid: 群号
    """
    js = json_load(curfew_path / gid / "config.json")
    js['time']['start_hour'] = time['hour']
    js['time']['start_minute'] = time['minute']
    json_write(curfew_path / gid / "config.json", js)


async def set_stop_time(gid: str, time: dict):
    """
    @param time: 时间
    @param gid: 群号
    """
    js = json_load(curfew_path / gid / "config.json")
    js['time']['stop_hour'] = time['hour']
    js['time']['stop_minute'] = time['minute']
    json_write(curfew_path / gid / "config.json", js)


async def get_time(gid: str) -> dict:
    js = json_load(curfew_path / gid / "config.json")
    return js['time']


async def ban_all(bot: Bot, gid: str):
    await bot.set_group_whole_ban(group_id=int(gid), enable=True)
    await bot.send_group_msg(group_id=int(gid), message=Message("宵禁啦!天干物燥,小心火烛~"))


async def unban_all(bot: Bot, gid: str):
    await bot.set_group_whole_ban(group_id=int(gid), enable=False)
    await bot.send_group_msg(group_id=int(gid), message=Message("今天又是元气满满的一天!"))


async def stop_all_task(gid: str):
    scheduler.remove_job(job_id=ban_all_task_id % gid)
    scheduler.remove_job(job_id=unban_all_task_id % gid)


async def start_task(bot: Bot, gid: str):
    """
    @param bot: Bot对象
    @param gid: 群号
    """
    time = await get_time(gid)
    start_hour = time['start_hour']
    start_minute = time['start_minute']
    stop_hour = time['stop_hour']
    stop_minute = time['stop_minute']
    scheduler.add_job(func=ban_all, id=ban_all_task_id % gid, trigger="cron", args=[bot, gid], hour=start_hour, minute=start_minute)
    scheduler.add_job(func=unban_all, id=unban_all_task_id % gid, trigger="cron", args=[bot, gid], hour=stop_hour, minute=stop_minute)


async def modify_task(gid: str):
    """
    @param gid: 群号
    """
    time = await get_time(gid)
    start_hour = time['start_hour']
    start_minute = time['start_minute']
    stop_hour = time['stop_hour']
    stop_minute = time['stop_minute']
    try:
        scheduler.reschedule_job(job_id=ban_all_task_id % gid, trigger="cron", hour=start_hour, minute=start_minute)
        scheduler.reschedule_job(job_id=unban_all_task_id % gid, trigger="cron", hour=stop_hour, minute=stop_minute)
    except apscheduler.jobstores.base.JobLookupError:
        pass


def resolve(msg: str):
    try:
        time = datetime.datetime.strptime(msg, format_str)
        return {"result": 1, "time": {"hour": time.hour, "minute": time.minute}}
    except:
        return {"result": 0}
