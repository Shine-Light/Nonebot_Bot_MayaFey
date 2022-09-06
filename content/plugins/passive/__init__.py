"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 20:35
"""
import json
import time

from nonebot import on_notice, on_request, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent, RequestEvent
from nonebot.exception import ActionFailed
from utils import database_mysql, users
from utils.other import add_target, translate
from utils.json_tools import json_write, json_load
from utils.path import friends_request_info
from . import rules


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "passive"),
    description="隐藏插件",
    usage="被动,无命令" + add_target(60)
)


cursor = database_mysql.cursor
db = database_mysql.connect
config = get_driver().config
superusers = config.superusers


# 管理员增加事件
admin_set = on_notice(rule=rules.checker_admin_set(), priority=4)
@admin_set.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    if uid not in config.superusers:
        gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
        users.update_role(gid, uid, "admin")


# 管理员减少事件
admin_unset = on_notice(rule=rules.checker_admin_unset(), priority=4)
@admin_unset.handle()
async def _(bot: Bot, event: NoticeEvent):
    uid = str(event.get_user_id())
    if uid not in config.superusers:
        gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
        users.update_role(gid, uid, "member")


# 超级用户邀请新用户事件
superuser_invite = on_request(rule=rules.checker_invite(), priority=4)
@superuser_invite.handle()
async def _(bot: Bot, event: NoticeEvent):
    await bot.set_group_add_request(
        flag=event.flag, sub_type="add", approve=True
    )


# 请求好友事件
admin_friend = on_request(rule=rules.checker_friend(), priority=4)
@admin_friend.handle()
async def _(bot: Bot, event: RequestEvent):
    uid = str(event.get_user_id())
    if uid in superusers:
        await bot.set_friend_add_request(
            flag=event.flag, approve=True
        )
    else:
        js = json_load(friends_request_info)
        des = json.loads(event.get_event_description().replace("'", '"'))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(des['time']))
        js.update({
                uid: {
                    "time": timestamp,
                    "comment": des['comment'],
                    "flag": des['flag']
                }
            })
        json_write(friends_request_info, js)
        nickname = (await bot.get_stranger_info(user_id=int(uid), no_cache=True))['nickname']
        for superuser in superusers:
            try:
                await bot.send_private_msg(
                    user_id=int(superuser),
                    message=f"收到 {nickname}({uid}) 的好友请求,请及时处理",
                    auto_escape=True
                )
            except ActionFailed:
                logger.error(f"向根用户 {superuser} 发起会话失败")
            except Exception as e:
                logger.error(f"发送好友请求提示失败,{str(e)}")


# 被根用户邀请入群事件
van_invite = on_request(rule=rules.checker_invite_group(), priority=4)
@van_invite.handle()
async def _(bot: Bot, event: RequestEvent):
    uid = str(event.get_user_id())
    gid = str(json.loads(event.get_event_description().replace("'", '"'))['group_id'])
    if uid in superusers:
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
