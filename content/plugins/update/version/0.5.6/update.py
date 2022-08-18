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
        last = ".py"
        if args:
            last = args[0]
        with open(dir_plugin + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    # def download_to_plugin_private(path, *args):
    #     last = ".py"
    #     if args:
    #         last = args[0]
    #     with open(dir_plugin_private + path + last, 'w+', encoding="utf-8") as file:
    #         file.write(requests.get(url_base + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_utils(path, *args):
        last = ".py"
        if args:
            last = args[0]
        with open(dir_utils + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "utils/" + path + last).content.decode("utf-8").replace("\r", ""))


    def download_to_root(path, url, *args):
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
        last = ".py"
        if args:
            last = args[0]
        with open(dir_hook + path + last, 'w+', encoding="utf-8") as file:
            file.write(requests.get(url_base + "hook/" + path + last).content.decode("utf-8").replace("\r", ""))


    # def download_to_resource(path, isBin, *args):
    #     last = ".json"
    #     if args:
    #         last = args[0]
    #     if isBin:
    #         mode = "wb+"
    #     else:
    #         mode = "w+"
    #     with open(dir_resource + path + last, mode, encoding="utf-8") as file:
    #         file.write(requests.get(url_base + "resource/" + path + last).content.decode("utf-8").replace("\r", ""))


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

    def download_img(dir_file: str, url: str):
        with open(dir_base + dir_file, "wb+") as file:
            file.write(requests.get(url).content)


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
    # with open(dir_base + "config/" + "total/" + "unable.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unable.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()

    # # 不可关闭列表更新
    # with open(dir_base + "config/" + "control/" + "unset.txt", "w+", encoding="utf-8") as file:
    #     file.write(requests.get("http://cdn.shinelight.xyz/nonebot/unset.txt").content.decode("utf-8").replace("\r", ""))
    #     file.close()

    # 更新部分
    download_readme()

    download_to_plugin("repeater/__init__")
    download_to_plugin("credit/__init__")
    download_to_plugin("credit/tools")

    download_to_hook("hook_enable")

    download_to_utils("path")
    download_to_utils("__init__")
    # 新增部分
    mkd("content/plugins/GenshinPray")
    mkd("content/plugins/GenshinPray/template")
    mkd("content/plugins/GenshinPray/template/role_up")
    mkd("content/plugins/GenshinPray/template/role_up/img")
    mkd("content/plugins/GenshinPray/template/role_up/img/avatar")
    mkd("content/plugins/GenshinPray/template/role_up/img/ele")
    mkd("content/plugins/GenshinPray/template/arm_up")
    mkd("content/plugins/GenshinPray/template/arm_up/img")
    mkd("content/plugins/GenshinPray/template/arm_up/spider")

    download_to_plugin("GenshinPray/__init__")
    download_to_plugin("GenshinPray/GenshinPray")
    download_to_plugin("GenshinPray/tools")
    download_to_plugin("GenshinPray/template/arm_up/1_8338b8e48022f6cb6f85", ".css")
    download_to_plugin("GenshinPray/template/arm_up/bundle_80bf8b862f1ee0d578e0", ".css")
    download_to_plugin("GenshinPray/template/arm_up/index", ".html")
    download_to_plugin("GenshinPray/template/arm_up/index copy", ".html")
    download_to_plugin("GenshinPray/template/arm_up/spider/in_img", ".txt")
    download_to_plugin("GenshinPray/template/arm_up/spider/in_name", ".txt")
    download_to_plugin("GenshinPray/template/arm_up/spider/down")
    run_py("content/plugins/GenshinPray/template/arm_up/spider/down.py")

    download_to_plugin("GenshinPray/template/role_up/1_8338b8e48022f6cb6f85", ".css")
    download_to_plugin("GenshinPray/template/role_up/bundle_80bf8b862f1ee0d578e0", ".css")
    download_to_plugin("GenshinPray/template/role_up/style", ".css")
    download_to_plugin("GenshinPray/template/role_up/index", ".html")
    download_to_plugin("GenshinPray/template/role_up/index copy", ".html")
    download_to_plugin("GenshinPray/template/role_up/img/avatar/name", ".txt")
    download_to_plugin("GenshinPray/template/role_up/img/ele/name", ".txt")
    download_to_plugin("GenshinPray/template/role_up/down")
    run_py("content/plugins/GenshinPray/template/role_up/down")

    download_img("content/plugins/GenshinPray/role_up/img/card-back.png",
                 "http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/img/card-back.png")
    download_img("content/plugins/GenshinPray/role_up/img/role-back-4star.png",
                 "http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/img/role-back-4star.png")
    download_img("content/plugins/GenshinPray/role_up/img/role-back-5star.png",
                 "http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/img/role-back-5star.png")
    # 结束

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
