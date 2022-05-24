"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:35
"""
import json
from threading import Timer

from nonebot import on_notice, on_request
from . import rules
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent, GroupRequestEvent
from utils import database_mysql, users
from .. import permission

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
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    role = users.get_role(gid, uid)
    if permission.tools.permission_(role, "superuser"):
        await bot.set_group_add_request(
            flag=event.flag, sub_type="invite", approve=True
        )

# group_lift_ban = on_notice(rule=rules.checker_unban(), priority=4)
# @group_lift_ban.handle()
# async def _(bot: Bot, event: NoticeEvent):
#     des = event.get_event_description().replace("'", '"')
#     des_js = json.loads(des)
#     uid = str(des_js['user_id'])
#     gid = str(des_js['group_id'])
#     users.update_role(gid, uid, 'member')
