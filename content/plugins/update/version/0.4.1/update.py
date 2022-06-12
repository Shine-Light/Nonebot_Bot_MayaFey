"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/6/12 11:51
"""
import json
import shutil

import requests
import os

# 路径处理
dir_path = os.path.dirname(os.path.abspath(__file__))
dir_path = dir_path.split("\\")
dir_path.pop(-1)
dir = ""
for a in dir_path:
    dir += a + "/"
version = requests.get("http://cdn.shinelight.xyz/nonebot/version.html").content.decode("utf-8")
dir_source = dir
dir_last = dir_source + version + "/"
dir_base = dir.replace(f"content/plugins/update/version/", "")
dir_plugin = dir_base + "content/plugins/"
dir_plugin_private = dir_base + "content/plugin_private/"
dir_utils = dir_base + "utils/"
url_base = "http://cdn.shinelight.xyz/nonebot/version/" + f"{version}/"

try:
    # 下载工具
    def download_to_plugin(path, *args):
        last = ".py"
        if args:
            last = args[0]
        with open(dir_plugin + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_plugin_private(path, *args):
        last = ".py"
        if args:
            last = args[0]
        with open(dir_plugin_private + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_utils(path, *args):
        last = ".py"
        if args:
            last = args[0]
        with open(dir_utils + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "utils/" + path + last).content.decode("utf-8").replace("\r", ""))


    # 翻译文件更新
    with open(dir_base + "config/" + "translate.json", "w+", encoding="utf-8") as file:
        file.write(requests.get("http://cdn.shinelight.xyz/nonebot/translate.json").content.decode("utf-8").replace("\r", ""))
        file.close()

    # 权限文件更新
    for f in os.listdir(dir_base + "config/" + "permission/" + "common"):
        name = f.split(".")[0]
        with open(dir_base + "config/" + "permission/" + "common/" + f"{name}.json", "w+", encoding="utf-8") as file:
            file.write(requests.get("http://cdn.shinelight.xyz/nonebot/permission_common.json").content.decode("utf-8").replace("\r", ""))
            file.close()

    for f in os.listdir(dir_base + "config/" + "permission/" + "special"):
        name = f.split(".")[0]
        with open(dir_base + "config/" + "permission/" + "special/" + f"{name}.json", "w+", encoding="utf-8") as file:
            file.write(requests.get("http://cdn.shinelight.xyz/nonebot/permission_special.json").content.decode("utf-8").replace("\r", ""))
            file.close()

    # # 不统计列表更新
    # with open(dir_base + "config/" + "total/" + "unable.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unable.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()
    #
    # # 不可关闭列表更新
    # with open(dir_base + "config/" + "control/" + "unset.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unset.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()

    # 更新部分
    download_to_plugin("admin/utils")
    download_to_plugin("ban_word/tools")
    download_to_plugin_private("execSql/__init__")
    download_to_plugin("menu/__init__")
    download_to_plugin("permission/__init__")
    download_to_plugin("permission/tools")
    download_to_plugin("repeater/__init__")
    download_to_plugin("update/__init__")
    download_to_plugin("update/tools")
    download_to_plugin("withdraw/__init__")
    download_to_plugin("word_cloud/__init__")

    download_to_utils("__init__")
    download_to_utils("hook_fast")
    download_to_utils("hook_permission")
    download_to_utils("hook_update")
    download_to_utils("other")
    download_to_utils("path")
    download_to_utils("url")

    # 新增部分
    os.mkdir(dir_plugin + "fortune")
    os.mkdir(dir_base + "config/fortune")
    download_to_plugin("fortune/__init__")
    download_to_plugin("fortune/config")
    download_to_plugin("fortune/data_source")
    download_to_plugin("fortune/utils")

    os.mkdir(dir_plugin + "morning")
    os.mkdir(dir_plugin + "morning/resource")
    os.mkdir(dir_base + "config/morning")
    download_to_plugin("morning/__init__")
    download_to_plugin("morning/data_source")
    download_to_plugin("morning/download")
    download_to_plugin("morning/resource/config", ".json")
    download_to_plugin("morning/resource/data", ".json")

    os.mkdir(dir_plugin + "what2eat")
    os.mkdir(dir_plugin + "what2eat/resource")
    download_to_plugin("what2eat/__init__")
    download_to_plugin("what2eat/config")
    download_to_plugin("what2eat/download")
    download_to_plugin("what2eat/utils")
    download_to_plugin("what2eat/resource/data", ".json")
    download_to_plugin("what2eat/resource/greating", ".json")
    # 结束

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
