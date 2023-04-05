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
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.log import logger

from utils import users, path, json_tools
from utils.admin_tools import banSb
from utils.permission import permission_
from utils.matcherManager import matcherManager


temp = {}
config = get_driver().config

@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot):
    if matcher.type != "message":
        return
    module_names = matcher.module_name
    if "init" in module_names or "utils" in module_names:
        return
    msg = event.get_plaintext()
    gid = str(event.group_id)
    uid = str(event.user_id)
    if "启用" in msg or "停用" in msg:
        return
    role = users.get_role(str(gid), uid)
    # 超级用户及以上不受限制
    if permission_(role, "superuser"):
        return
    # 不是命令信息,只能确认部分没有rule的on_message响应器
    if not matcher.rule.checkers:
        return

    conf = {}
    # 若Matcher已注册, 尝试获取Matcher的cd配置
    if matcherManager.isMatcherExist(matcher):
        matcher_name = matcherManager.getName(matcher)
        name_ = matcher_name
        conf = json_tools.json_load(path.cd_path / gid / "cd.json") \
            .get(matcher.plugin_name) \
            .get("matcher") \
            .get(matcher_name)

    # 不存在Matcher配置, 使用Plugin配置
    if not conf:
        name_ = matcher.plugin_name
        conf = json_tools.json_load(path.cd_path / gid / "cd.json") \
            .get(matcher.plugin_name) \
            .get("plugin")

    # 关闭cd
    if conf.get("time") <= 0 or conf.get("count") <= 0 or conf.get("ban_time") <= 0:
        return

    time_now: datetime.datetime = datetime.datetime.now()

    if not temp.get(gid):
        temp.update({gid: {}})
    if name_ not in temp.get(gid):
        temp.get(gid).update({name_: {}})
    if uid not in temp.get(gid).get(name_):
        print(temp.get(gid).get(name_))
        temp.get(gid).update({name_: {uid: {"time": time_now, "count": 1}}})
    else:
        try:
            time_past: datetime.datetime = temp.get(gid).get(name_).get(uid).get("time")
            time_delta = (time_now - time_past).seconds
            count = temp.get(gid).get(name_).get(uid).get("count")
            if time_delta <= conf.get("time") and count + 1 >= conf.get("count"):
                await banSb(gid, [int(uid)], time=conf.get('ban_time'))
                await bot.send(event, f"[{name_}] 触发的太快啦!冷静冷静,禁言 {conf.get('ban_time')}s", at_sender=True)
                temp.get(gid).get(name_).pop(uid)
                raise IgnoredException("恶意触发")
            elif time_delta > conf.get("time"):
                temp.get(gid).get(name_).pop(uid)
            else:
                temp.get(gid).get(name_).update({uid: {"time": time_now, "count": count + 1}})

        except KeyError as e:
            logger.error("恶意触发出错:" + str(e))
