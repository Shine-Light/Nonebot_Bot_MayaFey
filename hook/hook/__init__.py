"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/11 15:29
"""
from nonebot.plugin import PluginMetadata
from utils.other import add_target

from . import hook_enable, hook_fast, hook_lock, hook_total, hook_update, hook_permission, hook_reboot

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="hook",
    description="钩子函数",
    usage="被动, 无命令" + add_target(60),
    extra={
        "generate_type": "none",
        "author": "Shine_Light",
        "translate": "钩子函数",
    }
)