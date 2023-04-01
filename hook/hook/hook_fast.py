"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/1 21:29
"""
import datetime

from nonebot import get_driver
from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from utils import users, path
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from utils.admin_tools import banSb
from utils.permission import permission_
from nonebot.typing import T_State
from nonebot.log import logger

d = {}
unset: list = open(path.total_unable, "r", encoding="utf-8").read().split(",")
config = get_driver().config
try:
    fast_time = int(config.fast_time)
    fast_count = int(config.fast_count)
except:
    logger.warning("读取恶意触发配置失败,使用默认配置")
    fast_time = 10
    fast_count = 5

@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot, state: T_State):
    if matcher.type != "message":
        return
    module_names = matcher.module_name
    if "init" in module_names or "utils" in module_names:
        return
    msg = event.get_plaintext()
    if "启用" in msg or "停用" in msg:
        return
    plugin_name = matcher.plugin_name
    uid = str(event.user_id)
    gid = event.group_id
    time_now: datetime = datetime.datetime.now()
    role = users.get_role(str(gid), uid)

    # 超级用户及以上不受限制
    if permission_(role, "superuser"):
        return
    # 不触发插件
    if plugin_name in unset:
        return
    # 不是命令信息
    try:
        if not state["_prefix"]["raw_command"]:
            return
    except:
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
            if time_delta <= fast_time and count + 1 >= fast_count:
                await banSb(gid, [int(uid)], time=300)
                await bot.send(event, "检测到恶意触发,禁言5min", at_sender=True)
                d.pop(uid)
                raise IgnoredException("恶意触发")
            elif time_delta > 10:
                d.pop(uid)
            else:
                d.update({uid: {"time": time_now, "count": count + 1}})

        except KeyError:
            logger.error("恶意触发出错")
