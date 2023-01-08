"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/1/4 17:51
"""
from nonebot import get_driver
from nonebot.plugin import get_loaded_plugins
from nonebot.log import logger

from utils.config import manager

driver = get_driver()


@driver.on_startup
async def _():
    logger.info("开始初始化配置")
    for plugin in get_loaded_plugins():
        manager.addPluginConfig(plugin)
    logger.info("初始化配置结束")
