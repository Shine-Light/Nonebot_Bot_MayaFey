"""
Nonebot 2 Help Plugin
Author: XZhouQD
Since: 16 May 2021
"""
import nonebot
from .handler import helper
from utils.other import add_target


default_start = list(nonebot.get_driver().config.command_start)[0]

# Legacy way of self registering (use custom attributes)
# Deprecated for nonebot-plugin-help 0.3.1+, prefer PluginMetadata.extra['version']
__help_version__ = '0.3.1'
# Deprecated for nonebot-plugin-help 0.3.0+, prefer PluginMetadata.name
__help_plugin_name__ = "Nonebot2 Help Menu"
# Deprecated for nonebot-plugin-help 0.3.0+, prefer PluginMetadata.usage
__usage__ = f'''欢迎使用Nonebot2 Help Menu
本插件提供公共帮助菜单能力
此Bot配置的命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}
'''

# New way of self registering (use PluginMetadata)
__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name="help",
    description='Nonebot2轻量级帮助插件',
    usage=f'''欢迎使用Nonebot2 Help Menu
本插件提供公共帮助菜单能力
此Bot配置的命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}

获取本插件帮助: {default_start}帮助
展示已加载插件列表: {default_start}帮助 list
调取目标插件帮助信息: {default_start}帮助 {{插件名}}
''' + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "XZhouQD",
        "translate": "帮助",
    }
)
