"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 22:04
"""
import json

from nonebot import on_notice, on_command
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, Message
from nonebot.rule import Rule
from .. import utils, credit, permission
from . import tools
from ..utils.path import *
from ..utils import database_mysql, users


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


member_in = on_notice(rule=checker(), priority=5)
@member_in.handle()
async def _(bot: Bot, event: Event):
    des = event.get_event_description()
    data = json.loads(des.replace("'", '"'))
    gid = str(data['group_id'])
    uid = str(event.get_user_id())
    cursor.execute(f"SELECT alive FROM users WHERE gid='{gid}' and uid='{uid}'")
    re = cursor.fetchone()
    # 入群欢迎
    welcome_txt = welcome_path_base / f"{gid}.txt"
    message: str = open(welcome_txt, 'r', encoding="utf-8").read()
    # 回归欢迎
    if re:
        back_txt = back_path_base / f"{gid}.txt"
        message: str = open(back_txt, 'r', encoding="utf-8").read()

    await member_in.send(message=Message(message), at_sender=True)
    await utils.init(bot, event)
    await credit.tools.init(bot, event)


welcome_msg_update = on_command(cmd="入群欢迎", priority=7)
@welcome_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "welcome_msg_update", gid):
        content = str(event.get_message()).split(" ", 1)[1]
        if content:
            await tools.update(content, gid, "welcome")
            await welcome_msg_update.send("修改成功")
        else:
            await welcome_msg_update.send("指令有误")
    else:
        await welcome_msg_update.send("无权限")


back_msg_update = on_command(cmd="回归欢迎", aliases={"回群欢迎"}, priority=7)
@back_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "back_msg_update", gid):
        content = str(event.get_message()).split(" ", 1)[1]
        await tools.update(content, gid, "back")
        await welcome_msg_update.send("修改成功")
    else:
        await back_msg_update.send("无权限")
