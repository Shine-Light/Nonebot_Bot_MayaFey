"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 22:10
"""
import ujson as json
import os

from utils import json_tools
from utils.path import *

# 配置文件目录
config_url = config_path
# 插件目录
plugin_url = plugins_path
# 获取目录下文件夹
dirs = os.listdir(plugin_url)
# 插件列表
plugins: list = []
# 不可设置插件列表
unset: list = open(unset_path, 'r', encoding="utf-8").read().split(",")

async def init(gid: str):
    config_url_ = control_path / gid

    if not Path.exists(control_path):
        os.mkdir(control_path)

    if not Path.exists(config_url_):
        os.mkdir(config_url_)

    if not Path.exists(config_url_ / "control.json"):
        file = open(config_url_ / "control.json", "w", encoding="utf-8")
        file.write(json.dumps({"test": True}))
        file.close()

    # 配置文件
    plugin_config: dict = json_tools.json_load(config_url_ / "control.json")
    for file in dirs:
        if str(file) != '.idea' and str(file) != "__pycache__" and len(file.split('.')) == 1:
            plugins.append(file)

    for plugin in plugins:
        if str(plugin) not in plugin_config:
            plugin_config.update({str(plugin): True})

    with open(config_url_ / "control.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(plugin_config))


async def get_state(plugin: str, gid: str) -> bool:
    config_url_ = config_url / "control" / gid
    plugin_config: dict = json_tools.json_load(config_url_ / "control.json")
    return plugin_config[plugin]


async def is_unset(plugin: str) -> bool:
    """
    插件是否为不可设置插件
    plugin: 插件名
    """
    if plugin in unset:
        return True
    else:
        return False
