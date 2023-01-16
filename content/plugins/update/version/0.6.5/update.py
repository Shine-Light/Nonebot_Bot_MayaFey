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
dir_service = dir_base + "service/"
url_base = "http://cdn.shinelight.xyz/nonebot/version/" + f"{version}/"
url_base_resource = "http://cdn.shinelight.xyz/nonebot/resource/"

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
        try:
            with open(dir_plugin + path + last, 'w+', encoding="utf-8") as file:
                file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))
        except FileNotFoundError as exception:
                print(f"{str(exception)},跳过更新该文件")


    def download_to_plugin_private(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        try:
            last = ".py"
            if args:
                last = args[0]
            with open(dir_plugin_private + path + last, 'w+', encoding="utf-8") as file:
                file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))
        except FileNotFoundError as exception:
            print(f"{str(exception)},跳过该文件更新")


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

    def download_pyproject():
        download_to_root("pyproject", url_base + "pyproject", ".toml")

    def download_lock():
        download_to_root("poetry", url_base + "poetry", ".lock")


    def download_to_api(path, *args):
        last = ".py"
        if args:
            last = args[0]
        with open(dir_api + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "api/" + path + last).content.decode("utf-8").replace("\r", ""))


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


    def download_to_service(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        with open(dir_service + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "service/" + path + last).content.decode("utf-8").replace("\r", ""))


    # def download_to_resource(path, isBin, *args):
    #     last = ".json"
    #     if args:
    #         last = args[0]
    #     if isBin:
    #         with open(dir_resource + path + last, "wb+") as file:
    #             file.write(requests.get(url_base_resource + path + last).content)
    #     else:
    #         with open(dir_resource + path + last, "w+", encoding="utf-8") as file:
    #             file.write(requests.get(url_base_resource + path + last).content.decode("utf-8").replace("\r", ""))


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

    def remove_dir(path):
        try:
            shutil.rmtree(dir_base + path)
        except Exception as exception:
            print(f"{str(exception)} 跳过删除该文件夹")

    def remove_file(path):
        """
        @param path: 路径
        """
        try:
            os.remove(dir_base + path)
        except Exception as exception:
            print(f"{str(exception)} 跳过删除该文件")

    download_to_plugin("torment/__init__")
    download_to_plugin("schedule/tools")
    download_to_utils("json_tools")
    download_to_api("__init__")
    download_to_api("utils")
    download_to_utils("permission")
    download_to_plugin("schedule/__init__")
    download_to_plugin("gspanel/__init__")
    remove_file("content/plugins/memes/functions.py")
    remove_file("content/plugins/memes/gif_subtitle_meme.py")
    remove_file("content/plugins/memes/models.py")
    remove_file("content/plugins/memes/normal_meme.py")
    remove_file("content/plugins/permission/tools.py")
    download_to_utils("other")
    download_to_utils("url")
    download_to_plugin("credit/LuckyMoney")
    download_to_plugin("credit/__init__")
    mkd("content/plugins/credit/template")
    mkd("content/plugins/credit/template/assets")
    mkd("content/plugins/credit/template/css")
    mkd("content/plugins/credit/template/js")
    down_binary("content/plugins/credit/template/assets/regbag1_base.png", url_base_resource + "img/LuckyMoney/regbag1_base.png")
    down_binary("content/plugins/credit/template/assets/regbag_no_text.png", url_base_resource + "img/LuckyMoney/regbag_no_text.png")
    download_to_plugin("credit/template/css/style", ".css")
    download_to_plugin("credit/template/css/style2", ".css")
    download_to_plugin("credit/template/js/index2", ".js")
    download_to_plugin("credit/template/index", ".html")
    download_to_plugin("credit/template/index2", ".html")
    remove_dir("content/plugins/logo")
    download_to_plugin_private("execSql/__init__")
    mkd("service")
    download_to_service("ConfigInitial")
    download_to_service("__init__")
    download_to_utils("__init__")
    download_to_utils("config")
    download_to_utils("const")
    download_to_plugin("update/__init__")
    download_to_plugin("update/tools")
    download_to_plugin("repeater/__init__")
    download_to_plugin("epicfree/__init__")
    download_to_plugin("epicfree/data_source")
    download_to_plugin("welcome/__init__")
    download_to_plugin("leave/__init__")
    download_to_utils("admin_tools")
    download_to_plugin("question/__init__")
    download_to_hook("hook_enable")
    download_to_plugin("admin/__init__")
    download_to_plugin("speakrank/__init__")
    remove_dir("content/plugins/covid19")
    download_to_plugin("ban_word/__init__")
    download_to_plugin("ban_word/tools")
    mkd("content/plugin_private/sending")
    download_to_plugin_private("sending/__init__")
    download_to_plugin("menu/__init__")

    download_pyproject()
    download_readme()
    download_lock()

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
