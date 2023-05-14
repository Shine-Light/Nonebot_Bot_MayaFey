"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/1 21:42
"""
import ujson as json
import datetime

from nonebot import get_app, get_driver, require
from nonebot.plugin import PluginMetadata
from fastapi import FastAPI
from . import utils as api_utils
from .login import *
from .other import *
from .groups.admin import *
from .statistics import *
from .system import *
from .plugins import *
from .test import *
from utils.other import add_target
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="api",
    description="API",
    usage="被动, 无命令" + add_target(60),
    extra={
        "generate_type": "general",
        "author": "Shine_Light",
        "translate": "API",
        "configs_general": {
            "tokens": [],
            "expire": 1,
            "users": [
                {"username": "admin", "password": "12345678"}
            ]
        }
    }
)

app: FastAPI = get_app()
driver = get_driver()


@scheduler.scheduled_job(trigger="interval", hours=1, next_run_time=datetime.datetime.now() + datetime.timedelta(minutes=1))
async def _():
    await api_utils.clean_token()
