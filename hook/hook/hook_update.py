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
        target: dict = js['target']
        error = js["error"]
        if error:
            if target['target_type'] == "group":
                await bot.send_group_msg(message=f"更新中出错:{error}", group_id=target["target"])
            elif target['target_type'] == "private":
                await bot.send_private_msg(message=f"更新中出错:{error}", user_id=target["target"])
            if target['target_type'] == "api":
                json_tools.json_update(path.updating_path, "updating", False)
            else:
                json_tools.json_write(path.updating_path, {"updating": False, "error": "", "target": {"target": "", "target_type": ""}})
        else:
            try:
                with open("__version__", "w+", encoding="utf-8") as f:
                    f.write(await tools.get_version_last())
                json_tools.json_write(path.updating_path, {"updating": False, "error": "", "target": {"target": "", "target_type": ""}})

                msg = MessageSegment.image(await tools.get_update_log()) + MessageSegment.text("完整日志地址:https://mayafey.shinelight.xyz/updatelog/")
                if target['target_type'] == "group":
                    await bot.send_group_msg(message="更新成功,请自行执行一次初始化命令", group_id=target['target'])
                    await bot.send_group_msg(message=msg, group_id=target['target'])
                else:
                    if target['target_type'] == "private":
                        await bot.send_private_msg(message="更新成功,请自行执行一次初始化命令", user_id=target['target'])
                        await bot.send_private_msg(message=msg, user_id=target['target'])
            except Exception as e:
                if target['target_type'] == "group":
                    await bot.send_group_msg(message=f"更新日志发送失败,账号可能风控", group_id=target["target"])
                elif target['target_type'] == "private":
                    await bot.send_private_msg(message=f"更新日志发送失败,账号可能风控", user_id=target["target"])
                logger.error(str(e))
