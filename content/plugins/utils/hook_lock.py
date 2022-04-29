"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 20:41
"""
from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from ..plugin_control import funtions
from nonebot.adapters.onebot.v11 import GroupMessageEvent


# 插件开关检测
@run_preprocessor
async def lock_state(matcher: Matcher, event: GroupMessageEvent):
    module = matcher.module_name
    name = matcher.plugin_name
    if "utils" in module:
        return
    state: bool = await funtions.get_state(name, str(event.group_id))
    if not state:
        raise IgnoredException("插件已关闭")
