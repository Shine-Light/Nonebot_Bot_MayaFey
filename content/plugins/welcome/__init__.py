"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 22:04
"""
import json
import utils

from nonebot import on_notice, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, NoticeEvent, Event
from nonebot.rule import Rule
from nonebot.plugin import PluginMetadata
from . import tools
from utils.path import *
from utils import database_mysql, users

from utils.other import add_target, translate
from content.plugins.plugin_control import init as control_init
from content.plugins.credit.tools import init as credit_init
from content.plugins.permission.tools import special_per, get_special_per


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "welcome"),
    description="欢迎新人入群和老朋友回归",
    usage="/入群欢迎 {内容} (超级用户)\n"
          "/回群欢迎 {内容} (超级用户)" + add_target(60)
)


cursor = database_mysql.cursor
db = database_mysql.connect


# 入群检测
def checker():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_increase':
            return True

    return Rule(_checker)


member_in = on_notice(rule=checker(), priority=4)
@member_in.handle()
async def _(bot: Bot, event: NoticeEvent):
    if event.get_user_id() == bot.self_id:
        return
    des = event.get_event_description()
    data = json.loads(des.replace("'", '"'))
    gid = str(data['group_id'])
    uid = str(event.get_user_id())
    re = users.get_alive(gid, uid)
    # 入群欢迎
    welcome_txt = welcome_path_base / f"{gid}.txt"
    message: str = open(welcome_txt, 'r', encoding="utf-8").read()
    # 回归欢迎
    if re:
        cursor.execute(f"UPDATE users SET alive=TRUE WHERE uid='{uid}' AND gid='{gid}';")
        back_txt = back_path_base / f"{gid}.txt"
        message: str = open(back_txt, 'r', encoding="utf-8").read()
    await utils.init(bot, event)
    await credit_init(bot, event)
    await control_init(gid)
    await member_in.send(message=Message(message), at_sender=True)


welcome_msg_update = on_command(cmd="入群欢迎", priority=7)
@welcome_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "welcome_msg_update", gid):
        content = str(event.get_message()).split(" ", 1)[1]
        if content:
            await tools.update(content, gid, "welcome")
            await welcome_msg_update.send("修改成功")
        else:
            await welcome_msg_update.send("指令有误")
    else:
        await welcome_msg_update.finish(
        f"无权限,权限需在 {get_special_per(str(event.group_id), 'welcome_msg_update')} 及以上")


back_msg_update = on_command(cmd="回归欢迎", aliases={"回群欢迎"}, priority=7)
@back_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "back_msg_update", gid):
        content = str(event.get_message()).split(" ", 1)[1]
        await tools.update(content, gid, "back")
        await back_msg_update.send("修改成功")
    else:
        await back_msg_update.finish(
            f"无权限,权限需在 {get_special_per(str(event.group_id), 'back_msg_update')} 及以上")
