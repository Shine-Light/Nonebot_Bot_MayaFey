"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/10 15:43
"""
import json
import platform
import shutil
import aiofiles
import asyncio
import httpx
import os

# 路径处理
dir_path = os.path.dirname(os.path.abspath(__file__))
dir_path = dir_path.split("\\")
dir_path.pop(-1)
dir = ""
for a in dir_path:
    dir += a + "/"
version = httpx.get("http://cdn.shinelight.xyz/nonebot/version.html").content.decode("utf-8")
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
    async def request(url) -> str:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise Exception(f"非正常下载, 状态码: {resp.status_code}")
                else:
                    return resp.content.decode("utf-8").replace("\r", "")
        except Exception as e:
            print(f"下载 {url} 时出错, {str(e)}")
            return ""

    # 下载工具
    async def download_to_plugin(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        try:
            async with aiofiles.open(dir_plugin + path + last, 'w+', encoding="utf-8") as file:
                await file.write(await request(url_base + path + last))
        except FileNotFoundError as exception:
                print(f"{str(exception)},跳过更新该文件")


    async def download_to_plugin_private(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        try:
            last = ".py"
            if args:
                last = args[0]
            async with aiofiles.open(dir_plugin_private + path + last, 'w+', encoding="utf-8") as file:
                await file.write(await request(url_base + path + last))
        except FileNotFoundError as exception:
            print(f"{str(exception)},跳过该文件更新")


    async def download_to_utils(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        async with aiofiles.open(dir_utils + path + last, 'w+', encoding="utf-8") as file:
            await file.write(await request(url_base + "utils/" + path + last))


    async def download_to_root(path, url, *args):
        """
        @param path: 路径
        @param url: 链接
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        async with aiofiles.open(dir_base + path + last, 'w+', encoding="utf-8") as file:
            await file.write(await request(url + last))


    async def download_readme():
        await download_to_root("README", url_base + "README", ".md")

    async def download_pyproject():
        await download_to_root("pyproject", url_base + "pyproject", ".toml")

    async def download_lock():
        await download_to_root("poetry", url_base + "poetry", ".lock")


    async def download_to_api(path, *args):
        last = ".py"
        if args:
            last = args[0]
        async with aiofiles.open(dir_api + path + last, 'w+', encoding="utf-8") as file:
            await file.write(await request(url_base + "api/" + path + last))


    async def download_to_hook(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        async with aiofiles.open(dir_hook + path + last, 'w+', encoding="utf-8") as file:
            await file.write(await request(url_base + "hook/" + path + last))


    async def download_to_service(path, *args):
        """
        @param path: 路径
        @param args: 后缀
        """
        last = ".py"
        if args:
            last = args[0]
        async with aiofiles.open(dir_service + path + last, 'w+', encoding="utf-8") as file:
            await file.write(await request(url_base + "service/" + path + last))


    # async def download_to_resource(path, isBin, *args):
    #     last = ".json"
    #     if args:
    #         last = args[0]
    #     if isBin:
    #         async with aiofiles.open(dir_resource + path + last, "wb+") as file:
    #             await file.write(await request(url_base_resource + path + last).content)
    #     else:
    #         async with aiofiles.open(dir_resource + path + last, "w+", encoding="utf-8") as file:
    #             await file.write(await request(url_base_resource + path + last))


    async def mkd(folder: str):
        try:
            if os.path.exists(dir_base + folder):
                return
            else:
                os.mkdir(dir_base + folder)
        except Exception as e:
            print(f"创建文件 {folder} 失败, {str(e)}")

    # def rename(folder: str, dir_name: str):
    #     if os.path.exists(dir_base + dir_name):
    #         return
    #     os.rename(dir_base + folder, dir_base + dir_name)

    async def run_py(dir_file: str):
        dir_file = dir_base + dir_file
        if platform.system() == "Windows":
            os.system(f"python {dir_file}")
        else:
            os.system(f"python3 {dir_file}")

    async def down_binary(path, url):
        """
        @param path: 路径
        @param url: 链接
        """
        async with aiofiles.open(dir_base + path, "wb+") as file:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                content = resp.content
            await file.write(content)
            await file.close()

    async def remove_dir(path):
        try:
            shutil.rmtree(dir_base + path)
        except Exception as exception:
            print(f"{str(exception)} 跳过删除该文件夹")

    async def remove_file(path):
        """
        @param path: 路径
        """
        try:
            os.remove(dir_base + path)
        except Exception as exception:
            print(f"{str(exception)} 跳过删除该文件")

    async def main():
        await download_to_plugin("AI_talk/tools")
        await download_to_plugin("fortune/download")
        await download_to_plugin("ban_pic/__init__")
        await download_to_plugin("ban_word/__init__")
        await download_to_plugin("fortune/__init__")
        await download_to_plugin("perimssion/__init__")
        await download_to_hook("hook_perimssion")
        await download_to_utils("matcherManager")
        await download_to_utils("permission")
        await download_to_utils("users")
        await download_to_plugin("pic/__init__")
        await download_to_plugin("sign/__init__")
        await download_to_utils("requests_tools")

        await remove_file("hook/hook/hook_fast")
        await download_to_hook("hook_cd")

        await download_to_api("__init__")
        await download_to_plugin_private("execSql/__init__")
        await download_to_plugin_private("friends/__init__")
        await download_to_plugin("AI_talk/__init__")
        await download_to_plugin("DailyWife/__init__")
        await download_to_plugin("GenshinPray/__init__")
        await download_to_plugin("admin/__init__")
        await download_to_plugin("answersbook/__init__")
        await download_to_plugin("auto_baned/__init__")
        await download_to_plugin("ban_word/__init__")
        await download_to_plugin("blackjack/__init__")
        await download_to_plugin("credit/__init__")
        await download_to_plugin("curfew/__init__")
        await download_to_plugin("demerit/__init__")
        await download_to_plugin("enable/__init__")
        await download_to_plugin("epicfree/__init__")
        await download_to_plugin("gspanel/__init__")
        await download_to_plugin("guessMember/__init__")
        await download_to_plugin("help/__init__")
        await download_to_plugin("heweather/__init__")
        await download_to_plugin("ian/__init__")
        await download_to_plugin("leave/__init__")
        await download_to_plugin("memes/__init__")
        await download_to_plugin("menu/__init__")
        await download_to_plugin("morning/__init__")
        await download_to_plugin("nethot/__init__")
        await download_to_plugin("passive/__init__")
        await download_to_plugin("permission/__init__")
        await download_to_plugin("plugin_control/__init__")
        await download_to_plugin("question/__init__")
        await download_to_plugin("reboot/__init__")
        await download_to_plugin("repeater/__init__")
        await download_to_plugin("russian/__init__")
        await download_to_plugin("saymoney/__init__")
        await download_to_plugin("schedule/__init__")
        await download_to_plugin("simplemusic/__init__")
        await download_to_plugin("speakrank/__init__")
        await download_to_plugin("torment/__init__")
        await download_to_plugin("total/__init__")
        await download_to_plugin("translate_baidu/__init__")
        await download_to_plugin("translate_tencent/translator")
        await download_to_plugin("update/__init__")
        await download_to_plugin("welcome/__init__")
        await download_to_plugin("what2eat/__init__")
        await download_to_plugin("withdraw/__init__")
        await download_to_plugin("word_cloud/__init__")
        await download_to_hook("__init__")
        await download_to_service("ConfigInitial")
        await download_to_utils("__init__")
        await download_to_utils("path")
        
        await remove_dir("content/plugins/flash")
        await remove_dir("content/plugins/petpet")

        await download_to_plugin("heweather/weather_data")
        await download_to_utils("config")

        await download_to_plugin("memes/config")
        await remove_file("content/plugins/memes/data_source.py")
        await download_to_plugin("memes/depends")
        await remove_file("content/plugins/memes/download.py")
        await download_to_plugin("memes/exception")
        await download_to_plugin("memes/manager")
        await remove_file("content/plugins/memes/normal_memes.py")
        await remove_file("content/plugins/memes/gif_subtitle_memes.py")
        await download_to_plugin("memes/rule")
        await download_to_plugin("memes/utils")
        await mkd("content/plugins/memes/data_source")
        await download_to_plugin("memes/data_source/__init__")
        await download_to_plugin("memes/data_source/image_source")
        await download_to_plugin("memes/data_source/user_id")
        await download_to_plugin("memes/data_source/user_info")

        await download_pyproject()
        await download_readme()
        await download_lock()

    asyncio.run(main())

# 异常处理
except Exception as e:
    with open(dir_base + "config/" + "update/" + "updating.json", "r+", encoding="utf-8") as f:
        js = json.loads(f.read())
        js["error"] = str(e)

    with open(dir_base + "config/" + "update/" + "updating.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(js))
