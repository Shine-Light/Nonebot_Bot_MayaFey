"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:38
"""
import json
from utils import users
from utils.permission import permission_
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.rule import Rule


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


# 超级用户邀请新用户事件
def checker_invite():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values["post_type"] == "request" and values['request_type'] == 'group' and values['sub_type'] == 'add':
            uid = str(event.get_user_id())
            gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
            role = users.get_role(gid, uid)
            if permission_(role, "superuser"):
                return True

    return Rule(_checker)


# 好友事件
def checker_friend():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values["post_type"] == "request" and values["request_type"] == "friend":
            return True

    return Rule(_checker)


# 被邀请入群事件
def checker_invite_group():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values["post_type"] == "request" and values['request_type'] == 'group' and values['sub_type'] == 'invite':
            return True

    return Rule(_checker)


# 入群检测
def checker_group_increase():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_increase':
            return True

    return Rule(_checker)


# 退/离群检测
def checker_group_decrease():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_decrease':
            return True

    return Rule(_checker)
