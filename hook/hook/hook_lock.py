"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 20:41
"""
from nonebot.internal.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from content.plugins.plugin_control import functions
from nonebot.adapters.onebot.v11 import GroupMessageEvent


# 插件开关检测
@run_preprocessor
async def lock_state(matcher: Matcher, event: GroupMessageEvent):
    name = matcher.plugin_name
    msg = event.get_plaintext()
    module_names = matcher.module_name
    if "启用" in msg or "停用" in msg:
        return
    if "init" in module_names or "utils" in module_names or "enable" in module_names:
        return
    state: bool = await functions.get_state(name, str(event.group_id))
    if not state:
        raise IgnoredException("插件已关闭")
