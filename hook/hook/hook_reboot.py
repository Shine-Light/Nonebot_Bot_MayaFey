"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/22 17:32
"""
from nonebot.adapters.onebot.v11 import Bot
from utils import json_tools, path
from nonebot import get_driver

driver = get_driver()


@driver.on_bot_connect
async def rebooting(bot: Bot):
    js = json_tools.json_load(path.reboot_config_path)
    state: bool = js["rebooting"]
    if state:
        gid = js["gid"]
        js["rebooting"] = False
        js["gid"] = ""
        json_tools.json_write(path.reboot_config_path, js)
        await bot.send_group_msg(group_id=int(gid), message="重启成功")
