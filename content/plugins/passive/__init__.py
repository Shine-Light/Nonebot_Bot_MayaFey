"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:35
"""
import json
from threading import Timer

from nonebot import on_notice, on_request
from . import rules
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent, GroupRequestEvent, RequestEvent
from utils import database_mysql, users

cursor = database_mysql.cursor
db = database_mysql.connect


leave = on_notice(rule=rules.checker_leave(), priority=4)
@leave.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.member_leave(uid, gid)
    db.commit()


admin_set = on_notice(rule=rules.checker_admin_set(), priority=4)
@admin_set.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.update_role(gid, uid, "admin")


admin_unset = on_notice(rule=rules.checker_admin_unset(), priority=4)
@admin_unset.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.update_role(gid, uid, "member")


superuser_invite = on_request(rule=rules.checker_invite(), priority=4)
@superuser_invite.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    await bot.set_group_add_request(
        flag=event.flag, sub_type="invite", approve=True
    )

admin_friend = on_request(rule=rules.checker_friend(), priority=4)
@admin_friend.handle()
async def _(bot: Bot, event: RequestEvent):
    await bot.set_friend_add_request(
        flag=event.flag, approve=True
    )
