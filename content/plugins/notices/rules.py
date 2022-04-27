"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:38
"""
import json

from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.rule import Rule


# 退群检测
def checker_leave():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_decrease':
            return True

    return Rule(_checker)


# 管理增加检测
def checker_admin_set():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_admin' and values['sub_type'] == 'set':
            return True

    return Rule(_checker)


# 管理减少检测
def checker_admin_unset():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_admin' and values['sub_type'] == 'unset':
            return True

    return Rule(_checker)


# 禁言事件
def checker_baned():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_ban' and values['sub_type'] == 'ban':
            return True

    return Rule(_checker)


# 解除禁言事件
def checker_unban():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_ban' and values['sub_type'] == 'lift_ban':
            return True

    return Rule(_checker)


# 邀请事件
def checker_invite():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values["post_type"] == "request" and values['request_type'] == 'group' and values['sub_type'] == 'invite':
            return True

    return Rule(_checker)
