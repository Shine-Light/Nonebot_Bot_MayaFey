"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/30 21:03
"""
from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from utils.path import *
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from utils import json_tools
from utils import database_mysql
from content.plugins import permission
from nonebot.exception import IgnoredException


cursor = database_mysql.cursor
db = database_mysql.connect


@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot):
    # 只检查群聊的权限
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        uid = str(event.user_id)
        module_names = matcher.module_name.split('.')
        if "init" in module_names or "utils" in module_names:
            return
        cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' and gid='{gid}';")
        plugin_name = matcher.plugin_name
        role: str = cursor.fetchone()[0]
        permission_path = permission_base / "common" / f"{str(event.group_id)}.json"
        per: dict = json_tools.json_load(permission_path)
        if plugin_name in per:
            if permission.tools.permission_(role, per[plugin_name]):
                pass
            else:
                await bot.send(message=f"无权限,权限需在 {per[plugin_name]} 及以上", event=event)
                raise IgnoredException("无权限")

    else:
        pass

