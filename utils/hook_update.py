"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/21 13:09
"""
from nonebot.message import run_preprocessor
from nonebot.log import logger
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment
from utils import json_tools, path
from nonebot.exception import IgnoredException
from nonebot import get_driver
from content.plugins.update import tools

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
        error = js["error"]
        if error:
            await bot.send_group_msg(message=f"更新中出错:{error}", group_id=gid)
        else:
            try:
                with open("__version__", "w+", encoding="utf-8") as f:
                    f.write(await tools.get_version_last())

                json_tools.json_write(path.updating_path, {"updating": False, "error": "", "gid": ""})
                await bot.send_group_msg(message="更新成功,请自行执行一次初始化命令", group_id=gid)
                await bot.send_group_msg(message=Message([MessageSegment.image(await tools.get_update_log()),
                                                          MessageSegment.text(
                                                              "完整日志地址:http://cdn.shinelight.xyz/nonebot/log.md")]),
                                         group_id=gid)
            except Exception as e:
                await bot.send_group_msg(message=f"[hook_update] 更新日志发送失败:账号可能风控", group_id=gid)
                logger.error(str(e))
