"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/1 21:29
"""
import datetime

from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from ..utils import users
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from ..utils.admin_tools import banSb
from ..permission import tools


d = {}
unset = ["question", "ban_word", "word_cloud", "ban_pic"]


@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot):
    module_names = matcher.module_name
    if "init" in module_names or "utils" in module_names:
        return
    plugin_name = matcher.plugin_name
    uid = str(event.user_id)
    gid = event.group_id
    time_now: datetime = datetime.datetime.now()
    role = users.get_role(str(gid), uid)
    if tools.permission_(role, "superuser"):
        return
    if plugin_name not in unset:
        if not d:
            d.update({uid: {"time": time_now, "count": 1}})
        else:
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
                d.update({uid: {"time": time_past, "count": count + 1}})
