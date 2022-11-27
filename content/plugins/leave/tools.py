"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 13:23
"""
import os
import json


from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.rule import Rule
from utils.path import *
from utils.other import mk
from utils.json_tools import json_load


# 退群检测
def checker_leave():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_decrease':
            return True

    return Rule(_checker)


async def init(gid: str):
    leave_config_path = leave_base_path / gid / "config.json"
    if not (leave_base_path / gid).exists():
        (leave_base_path / gid).mkdir(exist_ok=True, parents=True)
    if not os.path.exists(leave_config_path):
        await mk("file", leave_config_path, "w", content=json.dumps(
            {"leave": "{leaved}({leaved_id}) 离开了",
             "kick": "{kicked}({kicked_id}) 被 {kicker}({kicker_id}) 踢出了"
             }))


async def update(content: str, gid: str, mode: str):
    leave_config_path = leave_base_path / gid / "config.json"
    js = json_load(leave_config_path)
    with open(leave_config_path, 'w+', encoding="utf-8") as file:
        if mode == 'leave':
            js.update({"leave": content})
            file.write(json.dumps(js, ensure_ascii=False))
        elif mode == 'kick':
            js.update({"kick": content})
            file.write(json.dumps(js, ensure_ascii=False))


async def get_text(gid: str, mode: str) -> str:
    leave_config_path = leave_base_path / gid / "config.json"
    js = json_load(leave_config_path)
    return js[mode]
