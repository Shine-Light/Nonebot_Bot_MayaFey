"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/22 15:57
"""
import random

from nonebot import require, get_bot, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.log import logger
from utils.path import torment_config_path
from utils.json_tools import json_load


driver = get_driver()
timezone = "Asia/Shanghai"
scheduler = require("nonebot_plugin_apscheduler").scheduler
state_ = {True: "开启", False: "关闭"}
mode_ = {"interval": "间隔", "cron": "定时"}


def get_config_text(gid):
    try:
        config = json_load(torment_config_path)
        state = state_[config[gid]["state"]]
        mode = mode_[config[gid]["mode"]]
        time = config[gid]["time"]
        text = f"状态: {state}\n" \
               f"模式: {mode}\n" \
               f"时间: {time}"
    except KeyError:
        text = "还没有配置过哦,无法查看配置情况"
    return text


async def torment(gid):
    count = 0
    try:
        bot: Bot = get_bot()
    except:
        # 避免刷屏
        count += 1
        if count % 10 == 0:
            logger.warning("等待机器人连接")
            return
    members: list = await bot.get_group_member_list(group_id=int(gid))
    while True:
        member = random.choice(members)
        # 不会随机到自己
        if member["user_id"] != int(bot.self_id):
            break
    await bot.send_group_msg(
                group_id=int(gid),
                message=Message([f"[CQ:poke,qq={member['user_id']}]"])
            )


async def add_cron_job(hour, minute, second, gid):
    scheduler.add_job(
        func=torment,
        trigger="cron",
        args=[gid],
        hour=hour,
        minute=minute,
        second=second,
        id=gid,
        timezone=timezone
    )


async def add_interval_job(hours, minutes, seconds, gid):
    scheduler.add_job(
        func=torment,
        trigger="interval",
        args=[gid],
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        id=gid,
        timezone=timezone
    )


async def add_job(gid):
    config = json_load(torment_config_path)
    mode = config[gid]["mode"]
    time = config[gid]["time"].split(":")
    if mode == "interval":
        hours, minutes, seconds = time
        await add_interval_job(hours, minutes, seconds, gid)
    elif mode == "cron":
        hour, minute, second = time
        await add_cron_job(hour, minute, second, gid)


async def remove_job(gid):
    scheduler.remove_job(gid)


async def modify_job(gid):
    config = json_load(torment_config_path)
    mode = config[gid]["mode"]
    time = config[gid]["time"].split(":")
    if mode == "interval":
        hours, minutes, seconds = time
        scheduler.reschedule_job(
            job_id=gid,
            trigger="interval",
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds)
        )
    elif mode == "cron":
        hour, minute, second = time
        scheduler.reschedule_job(
            job_id=gid,
            trigger="cron",
            hour=hour,
            minute=minute,
            second=second
        )


@driver.on_bot_connect
async def _():
    config = json_load(torment_config_path)
    for gid in config:
        state = config[gid]["state"]
        if state:
            await add_job(gid)



