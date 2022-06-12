"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/1 21:29
"""
import datetime

from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from utils import users,path
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from utils.admin_tools import banSb
from content.plugins.permission import tools
from nonebot.typing import T_State
from nonebot.log import logger

d = {}
unset: list = open(path.total_unable, "r", encoding="utf-8").read().split(",")


@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot, state: T_State):
    if matcher.type != "message":
        return
    module_names = matcher.module_name
    if "init" in module_names or "utils" in module_names:
        return
    plugin_name = matcher.plugin_name
    uid = str(event.user_id)
    gid = event.group_id
    time_now: datetime = datetime.datetime.now()
    role = users.get_role(str(gid), uid)

    # 超级用户及以上不受限制
    if tools.permission_(role, "superuser"):
        return
    # 不触发插件
    if plugin_name in unset:
        return
    # 不是命令信息
    if not state["_prefix"]["raw_command"]:
        return
    # 非命令信息优先级
    if matcher.priority not in range(1, 12):
        return

    if uid not in d:
        d.update({uid: {"time": time_now, "count": 1}})
    else:
        try:
            time_past: datetime = d[uid]['time']
            time_delta = (time_now - time_past).seconds
            count = d[uid]['count']
            if time_delta <= 10 and count + 1 >= 5:
                baning = banSb(gid, [int(uid)], time=300)
                async for ban in baning:
                    if ban:
                        await ban
                await bot.send(event, "检测到恶意触发,禁言5min", at_sender=True)
                d.pop(uid)
                raise IgnoredException("恶意触发")
            elif time_delta > 10:
                d.pop(uid)
            else:
                d.update({uid: {"time": time_now, "count": count + 1}})

        except KeyError:
            logger.error("恶意触发出错")
