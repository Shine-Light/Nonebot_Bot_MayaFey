"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 13:23
"""
import datetime
import json

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.rule import Rule
from utils.path import auto_baned_path
from utils.json_tools import json_load, json_write


config = get_driver().config

try:
    delta_time = int(config.auto_baned_delta_time)
except:
    delta_time = 10

# 退群检测
def checker_leave():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_decrease' and values['sub_type'] == 'leave':
            return True

    return Rule(_checker)


# 加群请求检测
def checker_group_request():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['post_type'] == 'request' and values['sub_type'] == 'add' and values['request_type'] == 'group':
            return True

    return Rule(_checker)


# 入群检测
def checker_in():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_increase':
            return True

    return Rule(_checker)


async def is_time_to_baned(uid: str, gid: str) -> bool:
    auto_baned_config_path = auto_baned_path / gid / "time.json"
    js = json_load(auto_baned_config_path)
    if uid in js:
        join_time = datetime.datetime.strptime(js[uid], "%Y-%m-%d %H:%M:%S")
        if (datetime.datetime.now() - join_time) < datetime.timedelta(minutes=delta_time):
            return True
    return False


async def is_baned(uid: str, gid: str) -> bool:
    auto_baned_config_path = auto_baned_path / gid / "baned.json"
    js = json_load(auto_baned_config_path)
    if uid in js:
        return True
    return False


async def baned_clean(bot: Bot):
    groups = await bot.get_group_list()
    for group in groups:
        try:
            gid = str(group['group_id'])
            auto_baned_config_path = auto_baned_path / gid / "time.json"
            js = json_load(auto_baned_config_path)
            for uid in set(js):
                join_time = datetime.datetime.strptime(js[uid], "%Y-%m-%d %H:%M:%S")
                if (datetime.datetime.now() - join_time) > datetime.timedelta(minutes=delta_time):
                    js.pop(uid)
            json_write(auto_baned_config_path, js)
        except FileNotFoundError:
            pass
