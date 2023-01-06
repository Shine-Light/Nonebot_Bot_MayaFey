"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/29 13:25
"""
import datetime
import ujson as json

from nonebot import get_bot, require, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.log import logger

from content.plugins.plugin_control.functions import get_state
from utils.path import schedule_path, schedule_groups_path
from utils.other import mk, get_bot_name
from utils.json_tools import json_write, json_load, json_update


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

driver = get_driver()
fmt_str_datetime = "%Y-%m-%d %H:%M:%S"
fmt_str_time = "%H:%M:%S"
time_mode = {"定时": "cron", "间隔": "interval", "日期": "date"}
mode_time = {"cron": "定时", "interval": "间隔", "date": "日期"}


async def job(gid: str, title: str):
    if get_state("schedule", gid):
        js = json_load(schedule_path / gid / "config.json")
        js = js[title]
        content = js["content"]
        count = 0
        try:
            bot: Bot = get_bot()
        except:
            # 避免刷屏
            count += 1
            if count % 10 == 0:
                logger.warning("等待机器人连接")
                return
        await bot.send_group_msg(group_id=int(gid), message=Message(content))


async def add_cron_job(title: str, time: list, gid: str):
    hour, minute, second = time
    scheduler.add_job(
        func=job,
        trigger="cron",
        hour=hour,
        minute=minute,
        second=second,
        args=[gid, title],
        id=f"{gid}_{title}"
    )


async def add_interval_job(title: str, time: list, gid: str):
    hours = int(time[0])
    minutes = int(time[1])
    seconds = int(time[2])
    scheduler.add_job(
        func=job,
        trigger="interval",
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        args=[gid, title],
        id=f"{gid}_{title}"
    )


async def add_date_job(title: str, time: str, gid: str):
    scheduler.add_job(
        func=job,
        trigger="date",
        run_date=time,
        args=[gid, title],
        id=f"{gid}_{title}"
    )


async def add_job(gid: str, title: str):
    js = json_load(schedule_path / gid / "config.json")
    js = js[title]
    mode = js["mode"]
    time = js["time"]
    if mode == "cron":
        await add_cron_job(title, time.split(":"), gid)
    elif mode == "interval":
        await add_interval_job(title, time.split(":"), gid)
    else:
        await add_date_job(title, time, gid)


async def modify_job(gid: str, title: str):
    js = json_load(schedule_path / gid / "config.json")
    js: dict = js[title]
    mode = js["mode"]
    if js.get("switch"):
        if mode == "cron":
            time = js["time"].split(":")
            hour, minute, second = time
            scheduler.reschedule_job(
                job_id=f"{gid}_{title}",
                trigger=mode,
                hour=hour,
                minute=minute,
                second=second
            )
        elif mode == "interval":
            time = js["time"].split(":")
            hours, minutes, seconds = time
            scheduler.reschedule_job(
                job_id=f"{gid}_{title}",
                trigger=mode,
                hours=hours,
                minutes=minutes,
                seconds=seconds
            )
        else:
            time = js["time"]
            scheduler.reschedule_job(
                job_id=f"{gid}_{title}",
                trigger=mode,
                run_date=time
            )


async def delete_job(gid: str, title: str):
    js = json_load(schedule_path / gid / "config.json")
    js.pop(title)
    json_write(schedule_path / gid / "config.json", js)
    scheduler.remove_job(f"{gid}_{title}")


async def job_on(gid: str, title: str):
    """
    开启定时任务
    gid: 群号
    title: 任务标题
    """
    job_id = f"{gid}_{title}"
    if not scheduler.get_job(job_id):
        await add_job(gid, title)
    js = json_load(schedule_path / gid / "config.json")[title]
    js.update({"switch": True})
    json_update(schedule_path / gid / "config.json", title, js)


async def job_off(gid: str, title: str):
    """
    关闭定时任务
    gid: 群号
    title: 任务标题
    """
    job_id = f"{gid}_{title}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    js = json_load(schedule_path / gid / "config.json")[title]
    js.update({"switch": False})
    json_update(schedule_path / gid / "config.json", title, js)


async def schedule_init(gid: str):
    schedule_config_path = schedule_path / gid / "config.json"
    if not (schedule_path / gid).exists():
        (schedule_path / gid).mkdir(exist_ok=True, parents=True)
    if not schedule_config_path.exists():
        await mk("file", schedule_config_path, 'w', content=json.dumps({}))
    if not schedule_groups_path.exists():
        await mk("file", schedule_groups_path, 'w', content=gid + "\n")
    if gid not in open(schedule_groups_path, "r", encoding="utf-8").read():
        open(schedule_groups_path, "a", encoding="utf-8").write(gid + "\n")


@driver.on_bot_connect
async def _():
    try:
        await clean_out_job()
        for gid in open(schedule_groups_path, "r", encoding="utf-8").read().strip().split("\n"):
            js = json_load(schedule_path / gid / "config.json")
            for title in js:
                await add_job(gid, title)
    except:
        pass


async def clean_out_job():
    try:
        for gid in open(schedule_groups_path, "r", encoding="utf-8").read().strip().split("\n"):
            js = json_load(schedule_path / gid / "config.json")
            for title in js:
                if js[title]["mode"] == "date":
                    if datetime.datetime.now() > datetime.datetime.strptime(js[title]["time"], fmt_str_datetime):
                        try:
                            await delete_job(gid, title)
                        except:
                            pass
    except FileNotFoundError:
        pass


async def save(js: dict, gid: str):
    schedule_config_path = schedule_path / gid / "config.json"
    src_js = json_load(schedule_config_path)
    title = js["title"]
    src_js.update({title: js})
    json_write(schedule_config_path, src_js)


async def title_is_exists(gid: str, title: str) -> bool:
    schedule_config_path = schedule_path / gid / "config.json"
    js = json_load(schedule_config_path)
    if title in js:
        return True
    return False


async def get_schedule_plaintext(js: dict) -> str:
    msg = ""
    for title in js:
        mode = js[title]["mode"]
        time = js[title]["time"]
        msg += f"任务标题: {title}\n"
        msg += f"\t模式: {mode_time[mode]}\n"
        msg += f"\t时间: {time}\n"
    return msg.strip()


async def get_schedule_list(gid: str) -> dict:
    await clean_out_job()
    schedule_config_path = schedule_path / gid / "config.json"
    js = json_load(schedule_config_path)
    return js


async def raw_msg_checker(raw_msg: str, gid: str) -> dict:
    await schedule_init(gid)
    if len(raw_msg.split(" ")) not in [4, 5, 6]:
        return {"state": "error", "error": "参数格式错误了,检查一下吧"}

    title = raw_msg.split(" ")[1]
    if not title.strip():
        return {"state": "error", "error": "标题不能为空哦"}

    mode = raw_msg.split(" ")[2]
    if mode not in time_mode:
        return {"state": "error", "error": f"没有 {mode} 模式"}
    else:
        mode = time_mode[mode]

    if mode == "date":
        try:
            time = raw_msg.split(" ")[3].strip() + " " + raw_msg.split(" ")[4].strip()
            if datetime.datetime.strptime(time, fmt_str_datetime) < datetime.datetime.now():
                return {"state": "error", "error": "这个时间已经过去了哦"}
        except:
            return {"state": "error", "error": "时间格式不对哦,日期格式应为 `年-月-日 时:分:秒`"}
    else:
        try:
            if len(raw_msg.split(" ")) not in [4, 5]:
                return {"state": "error", "error": "时间格式不对哦, 格式应为 `时:分:秒`"}
            time = raw_msg.split(" ")[3].strip()
            temp = datetime.datetime.strptime(time, fmt_str_time)
            temp_base = datetime.datetime.strptime("00:00:00", fmt_str_time)
            delta = temp - temp_base
            if mode == "interval" and delta.seconds <= 0:
                return {"state": "error", "error": f"你想累死{get_bot_name()}吗?间隔最少1秒啦!"}
        except:
            return {"state": "error", "error": "时间格式不对哦, 格式应为 `时:分:秒`?间隔最少1秒啦!"}

    try:
        if len(raw_msg.split(" ")) == 6:
            content = raw_msg.split(" ")[5].strip()
        else:
            content = raw_msg.split(" ")[4].strip()
    except:
        content = ""

    return {
        "state": "success",
        "data":
        {
                "title": title,
                "mode": mode,
                "time": time,
                "content": content
            }
        }
