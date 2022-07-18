"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/4 20:36
"""
import os
from utils.path import plugin_path
from content.plugins.permission.tools import get_plugin_permission, role_cn
from content.plugins.total.tools import get_count
from content.plugins.plugin_control.functions import get_state, is_unset
from utils.other import translate


async def get_plugin_list() -> list:
    plugins = []
    dirs = os.listdir(plugin_path)
    for file in dirs:
        if str(file) != '.idea' and str(file) != "__pycache__" and len(file.split('.')) == 1:
            plugins.append(file)
    return plugins


async def get_plugin_detail(gid: str, plugin: str) -> dict:
    permission = role_cn(get_plugin_permission(gid, plugin))
    count = await get_count(gid, plugin)
    state = await get_state(plugin, gid)
    unset = await is_unset(plugin)
    if state:
        state = "开"
    else:
        state = "关"
    if unset:
        unset = "是"
    else:
        unset = "否"
    cn = translate("e2c", plugin)
    return {"name": cn, "state": state, "count": count, "permission": permission, "unset": unset}
