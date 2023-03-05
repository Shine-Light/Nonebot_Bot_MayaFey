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

    def run_py(dir_file: str):
        dir_file = dir_base + dir_file
        if platform.system() == "Windows":
            os.system(f"python {dir_file}")
        else:
            os.system(f"python3 {dir_file}")

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

    download_to_plugin("question/__init__")
    download_to_utils("database_mysql")
    download_to_utils("admin_tools")
    download_to_plugin("repeater/__init__")
    download_to_plugin("curfew/__init__")
    download_to_utils("__init__")
    remove_file("content/plugins/admin/utils.py")
    download_to_hook("hook_permission")
    download_to_utils("permission")
    download_to_root("bot", url_base + "bot")
    download_to_plugin("ban_word/tools")
    download_to_plugin("update/__init__")
    download_to_root("config/permission/permissions", url_base + "config/permission/permissions", ".json")
    download_to_utils("path")
    download_to_utils("users")
    download_to_plugin("permission/__init__")
    download_to_plugin("GenshinPray/template/arm_up/spider/down")
    download_to_plugin("GenshinPray/template/arm_up/spider/in_img", ".txt")
    download_to_plugin("GenshinPray/template/arm_up/spider/in_name", ".txt")
    run_py("content/plugins/GenshinPray/template/arm_up/spider/down.py")
    download_to_plugin("GenshinPray/template/role_up/down")
    download_to_plugin("GenshinPray/template/role_up/img/avatar/name", ".txt")
    run_py("content/plugins/GenshinPray/template/role_up/down.py")
    download_to_utils("config")
    download_to_plugin("fortune/__init__")
    download_to_plugin("fortune/config")
    download_to_plugin("fortune/data_source")
    download_to_plugin("fortune/download")
    download_to_plugin("fortune/utils")
    download_to_root("config/fortune/specific_rules", url_base + "config/fortune/specific_rules", ".json")

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
