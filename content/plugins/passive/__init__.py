"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:35
"""
import json

from nonebot import on_notice, on_request
from nonebot.plugin import PluginMetadata

from nonebot.adapters.onebot.v11 import Bot, NoticeEvent, GroupRequestEvent, RequestEvent
from utils import database_mysql, users
from content.plugins.permission.tools import permission_

from utils.other import add_target, translate
from . import rules


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "passive"),
    description="隐藏插件",
    usage="被动,无命令" + add_target(60)
)


cursor = database_mysql.cursor
db = database_mysql.connect


# 离群事件
leave = on_notice(rule=rules.checker_leave(), priority=4)
@leave.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.member_leave(uid, gid)
    db.commit()


# 管理员增加事件
admin_set = on_notice(rule=rules.checker_admin_set(), priority=4)
@admin_set.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.update_role(gid, uid, "admin")


# 管理员减少事件
admin_unset = on_notice(rule=rules.checker_admin_unset(), priority=4)
@admin_unset.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    users.update_role(gid, uid, "member")


# 超级用户邀请新用户事件
superuser_invite = on_request(rule=rules.checker_invite(), priority=4)
@superuser_invite.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    await bot.set_group_add_request(
        flag=event.flag, sub_type="add", approve=True
    )


# 管理员请求好友事件
admin_friend = on_request(rule=rules.checker_friend(), priority=4)
@admin_friend.handle()
async def _(bot: Bot, event: RequestEvent):
    await bot.set_friend_add_request(
        flag=event.flag, approve=True
    )


# 根用户邀请入群事件
van_invite = on_request(rule=rules.checker_invite_group(), priority=4)
@van_invite.handle()
async def _(bot: Bot, event: RequestEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    role = users.get_role(gid, uid)
    if permission_(role, "Van"):
        try:
            await bot.set_group_add_request(
                flag=event.flag, sub_type="invite", approve=True
            )
        except:
            pass
    else:
        try:
            await bot.set_group_add_request(
                flag=event.flag, sub_type="invite", approve=False, reason="无权限"
            )
        except:
            try:
                await bot.set_group_leave(group_id=int(gid), is_dismiss=False)
            except:
                pass
