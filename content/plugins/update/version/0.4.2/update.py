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
    # 工具
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


    def mkd(folder: str):
        if os.path.exists(folder):
            return
        else:
            os.mkdir(folder)


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

    # 不统计列表更新
    with open(dir_base + "config/" + "total/" + "unable.txt", "w+", encoding="utf-8") as file:
        file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unable.txt").content.decode("utf-8").replace("\r", ""))
        file.close()

    # # 不可关闭列表更新
    # with open(dir_base + "config/" + "control/" + "unset.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unset.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()

    # 更新部分
    download_to_plugin("admin/__init__")
    download_to_plugin("admin/config")

    download_to_plugin("ban_word/__init__")

    download_to_plugin("heweather/__init__")
    download_to_plugin("heweather/config")
    download_to_plugin("heweather/model")
    download_to_plugin("heweather/render_pic")
    download_to_plugin("heweather/weather_data")

    download_to_plugin("menu/__init__")

    download_to_plugin("permission/tools")

    download_to_plugin("pic/__init__")

    download_to_plugin("plugin_control/functions")

    download_to_plugin("saymoney/__init__")

    download_to_plugin("pic/__init__")

    download_to_plugin("sign/__init__")

    download_to_plugin("welcome/__init__")

    download_to_plugin("word_cloud/__init__")
    download_to_plugin("word_cloud/tools")

    download_to_utils("htmlrender/__init__")
    download_to_utils("htmlrender/browser")
    download_to_utils("htmlrender/data_source")
    download_to_utils("__init__")
    download_to_utils("admin_tools")
    download_to_utils("path")
    download_to_utils("requests_tools")
    download_to_utils("users")
    # 新增部分
    mkd(dir_plugin + "demerit")
    download_to_plugin("demerit/__init__")
    download_to_plugin("demerit/tools")

    mkd(dir_plugin + "speakrank")
    download_to_plugin("speakrank/__init__")
    # 结束

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
