"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/10 15:43
"""
import json
import platform
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
dir_api = dir_base + "Api/api/"
dir_hook = dir_base + "hook/hook/"
dir_resource = dir_base + "resource/"
url_base = "http://cdn.shinelight.xyz/nonebot/version/" + f"{version}/"

try:
    # 下载工具
    def download_to_plugin(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        with open(dir_plugin + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    # def download_to_plugin_private(path, *args):
    #     """
    #     @param path: 路径
    #     @param args: 后缀
    #     """
    #     last = ".py"
    #     if args:
    #         last = args[0]
    #     with open(dir_plugin_private + path + last, 'w+', encoding="utf-8") as file:
    #         file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_utils(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        with open(dir_utils + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "utils/" + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_root(path, url, *args):
        """
        @param path: 路径
        @param url: 链接
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        with open(dir_base + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url + last).content.decode("utf-8").replace("\r", ""))


    def download_readme():
        download_to_root("README", url_base + "README", ".md")


    # def download_to_api(path, *args):
    #     last = ".py"
    #     if args:
    #         last = args[0]
    #     with open(dir_api + path + last, 'w+', encoding="utf-8") as file:
    #         file.write(requests.get(url_base + "api/" + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_hook(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        with open(dir_hook + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "hook/" + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_resource(path, isBin, *args):
        last = ".json"
        if args:
            last = args[0]
        if isBin:
            mode = "wb+"
            with open(dir_resource + path + last, mode) as file:
                file.write(requests.get(url_base + "resource/" + path + last).content)
        else:
            mode = "w+"
            with open(dir_resource + path + last, mode, encoding="utf-8") as file:
                file.write(requests.get(url_base + "resource/" + path + last).content.decode("utf-8").replace("\r", ""))


    def mkd(folder: str):
        if os.path.exists(dir_base + folder):
            return
        else:
            os.mkdir(dir_base + folder)

    # def rename(folder: str, dir_name: str):
    #     if os.path.exists(dir_base + dir_name):
    #         return
    #     os.rename(dir_base + folder, dir_base + dir_name)

    # def run_py(dir_file: str):
    #     dir_file = dir_base + dir_file
    #     if platform.system() == "Windows":
    #         os.system(f"python {dir_file}")
    #     else:
    #         os.system(f"python3 {dir_file}")

    def down_binary(path, url):
        """
        @param path: 路径
        @param url: 链接
        """
        with open(dir_base + path, "wb+") as file:
            file.write(requests.get(url).content)
            file.close()


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

    # for f in os.listdir(dir_base + "config/" + "permission/" + "special"):
    #     name = f.split(".")[0]
    #     with open(dir_base + "config/" + "permission/" + "special/" + f"{name}.json", "w+", encoding="utf-8") as file:
    #         file.write(requests.get("http://cdn.shinelight.xyz/nonebot/permission_special.json").content.decode("utf-8").replace("\r", ""))
    #         file.close()

    # 不统计列表更新
    with open(dir_base + "config/" + "total/" + "unable.txt", "w+", encoding="utf-8") as file:
        file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unable.txt").content.decode("utf-8").replace("\r", ""))
        file.close()

    # 不可关闭列表更新
    # with open(dir_base + "config/" + "control/" + "unset.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unset.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()

    # 更新部分
    download_readme()
    download_to_plugin("AI_talk/__init__")
    download_to_plugin("ban_word/__init__")
    download_to_plugin("covid19/__init__")
    download_to_plugin("covid19/data")
    download_to_plugin("covid19/data_load")
    download_to_plugin("covid19/policy")
    download_to_plugin("covid19/uilts")
    download_to_plugin("covid19/tools")
    download_to_plugin("credit/tools")
    download_to_plugin("demerit/__init__")
    download_to_plugin("flash/__init__")
    download_to_plugin("leave/__init__")
    download_to_plugin("menu/__init__")
    download_to_plugin("passive/__init__")
    download_to_plugin("repeater/__init__")
    download_to_plugin("question/__init__")
    download_to_plugin("schedule/tools")
    download_to_plugin("sign/tools")
    download_to_plugin("speakrank/__init__")
    download_to_plugin("torment/__init__")
    download_to_plugin("welcome/__init__")
    download_to_plugin("withdraw/__init__")
    download_to_plugin("word_cloud/__init__")

    download_to_hook("hook_fast")

    download_to_utils("__init__")
    download_to_utils("other")
    download_to_utils("path")
    download_to_utils("users")

    download_to_resource("font/MSYH", True, ".TTC")
    # 新增部分
    mkd("content/plugins/auto_baned")
    download_to_plugin("auto_baned/__init__")
    download_to_plugin("auto_baned/tools")
    # 结束

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
