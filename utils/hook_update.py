"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/21 13:09
"""
import json
import os
import platform
import shutil

from nonebot.message import run_preprocessor
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment
from ..utils import json_tools, path
from nonebot.exception import IgnoredException
from nonebot import get_driver
from ..update import tools

driver = get_driver()


@run_preprocessor
async def check_updating(matcher: Matcher, event: GroupMessageEvent):
    module_names = matcher.module_name
    if "init" in module_names or "utils" in module_names:
        return
    state: bool = json_tools.json_load(path.updating_path)['updating']
    if state:
        raise IgnoredException("机器人正在更新,无法使用")


@driver.on_bot_connect
async def updating(bot: Bot):
    js = json_tools.json_load(path.updating_path)
    state: bool = js["updating"]
    if state:
        gid = int(js['gid'])
        # await utils.init(bot, event)
        for dir in os.listdir(path.update_path / "version"):
            version_old = str(dir)
            version_last = str(await tools.get_version_last())
            if version_old != version_last:
                if platform.system() == "Windows":
                    shutil.rmtree(str(path.update_path / "version" / version_old).replace("/", "\\"))
                else:
                    shutil.rmtree(str(path.update_path / "version" / version_old))
        try:
            json_tools.json_write(path.updating_path, {"updating": False, "error": "", "gid": ""})
            await bot.send_group_msg(message="更新成功,请自行执行一次初始化命令", group_id=gid)
            await bot.send_group_msg(message=Message([MessageSegment.image(await tools.get_update_log()),
                                                      MessageSegment.text(
                                                          "完整日志地址:http://cdn.shinelight.xyz/nonebot/log.md")]),
                                     group_id=gid)
        except Exception as e:
            await bot.send_group_msg(message=f"更新出错:{str(e)}", group_id=gid)
