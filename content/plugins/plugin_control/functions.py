"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 22:10
"""
import json
import os

from utils import json_tools
from utils.path import *

# 配置文件目录
config_url = config_path
# 插件目录
plugin_url = plugin_path
# 获取目录下文件夹
dirs = os.listdir(plugin_url)
# 插件列表
plugins: list = []


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



def translate(mode: str, name: str) -> str:
    """
    插件名称翻译
    mode: e2c(英译中) c2e(中译英)
    name: 插件名
    """
    # 翻译文件
    plugin_translate: dict = json_tools.json_load(config_url / "translate.json")
    # e2c 英译中
    if mode == 'e2c':
        if name not in plugin_translate:
            return name
        for name_en in plugin_translate:
            if name == name_en:
                return plugin_translate[name_en]

    # c2e 中译英
    elif mode == 'c2e':
        for name_en in plugin_translate:
            if plugin_translate[name_en] == name:
                return name_en
        return name

    else:
        return name
