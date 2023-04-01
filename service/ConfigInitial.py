"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/1/4 17:51
"""
from nonebot import get_driver
from nonebot.plugin import get_loaded_plugins, PluginMetadata
from nonebot.log import logger

from utils.config import manager
from utils.other import add_target

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="ConfigInitial",
    description="配置初始化",
    usage="被动, 无命令" + add_target(60),
    extra={
        "generate_type": "none",
        "author": "Shine_Light",
        "translate": "配置初始化",
    }
)

driver = get_driver()


@driver.on_startup
async def _():
    logger.info("开始初始化配置")
    for plugin in get_loaded_plugins():
        manager.addPluginConfig(plugin)
    logger.info("初始化配置结束")
