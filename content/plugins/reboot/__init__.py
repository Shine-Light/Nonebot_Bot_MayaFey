"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/22 17:26
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from utils.other import reboot as reboot_, add_target, translate
from utils.json_tools import json_load, json_write
from utils.path import reboot_config_path


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "reboot"),
    description="重启机器人",
    usage="/重启" + add_target(60)
)


reboot = on_command("重启", aliases={"reboot"}, permission=SUPERUSER, priority=1)
@reboot.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    js = json_load(reboot_config_path)
    js.update({"rebooting": True, "gid": gid})
    json_write(reboot_config_path, js)
    await reboot.send("正在重启")
    reboot_()
