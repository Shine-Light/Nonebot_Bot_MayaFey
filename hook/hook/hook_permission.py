"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/30 21:03
"""
from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from utils.path import *
from utils import json_tools, users
from nonebot.exception import IgnoredException
from utils.permission import permission_, special_per, get_special_per, have_special_per
from utils.matcherManager import matcherManager
from utils.users import get_role


# Plugin级别权限控制
@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot):
    # 只检查群聊的权限
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
        uid = str(event.user_id)
        module_names = matcher.module_name.split('.')
        msg = event.get_plaintext()
        if "init" in module_names or "utils" in module_names:
            return
        if "启用" in msg or "停用" in msg:
            return
        # 非命令响应器
        if not matcher.rule.checkers:
            return
        plugin_name = matcher.plugin_name
        role: str = users.get_role(gid, uid)
        permission_path = permission_base / "common" / f"{str(event.group_id)}.json"
        per: dict = json_tools.json_load(permission_path)
        if plugin_name in per:
            if permission_(role, per[plugin_name]):
                pass
            else:
                await bot.send(message=f"[{matcher.plugin.name}] 无权限,权限需在 {per[plugin_name]} 及以上", event=event)
                raise IgnoredException(f"{uid} 无权限使用 {plugin_name}")

    else:
        pass


# Matcher级别权限控制
@run_preprocessor
async def _(matcher: Matcher, event: GroupMessageEvent, bot: Bot):
    gid = str(event.group_id)
    module_names = matcher.module_name.split('.')
    msg = event.get_plaintext()
    if "init" in module_names or "utils" in module_names:
        return
    if "启用" in msg or "停用" in msg:
        return
    if not matcherManager.isMatcherExist(matcher):
        return
    per_name = matcherManager.getName(matcher)
    if have_special_per(per_name, gid):
        if not special_per(
                get_role(gid, str(event.user_id)),
                per_name,
                gid
        ):
            await bot.send_group_msg(
                group_id=event.group_id,
                message=f"[{matcher.__matcher_name__}] 无权限,权限需在 {get_special_per(gid, per_name)} 及以上"
            )
            logger.debug(f"Matcher权限检测 权限不足")
            raise IgnoredException("权限不足")
