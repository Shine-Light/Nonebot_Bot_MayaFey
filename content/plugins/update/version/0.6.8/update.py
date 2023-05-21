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
        await download_to_plugin("GenshinPray/template/role_up/img/avatar/name", ".txt")
        await run_py("content/plugins/GenshinPray/template/role_up/down.py")

        await download_to_plugin("admin/__init__")
        await download_to_utils("admin_tools")
        await download_to_utils("const")
        await download_to_utils("users")
        await download_to_hook("hook_enable")
        await download_to_utils("__init__")
        await download_to_utils("json_tools")
        await download_to_plugin("passive/__init__")
        await download_to_plugin("morning/__init__")
        await download_to_plugin("translate_tencent/__init__")
        await download_to_plugin("translate_tencent/translator")
        await download_to_plugin("total/__init__")
        await download_to_hook("hook_total")
        await download_to_plugin("memes/__init__")
        await download_to_plugin("speakrank/__init__")
        await download_to_utils("permission")
        await download_to_utils("config")
        await download_to_hook("hook_update")
        await download_to_plugin("update/__init__")
        await download_to_plugin("update/tools")

        await download_to_api("__init__")
        await download_to_api("exception")
        await download_to_api("model")
        await download_to_api("utils")
        await mkd("Api/api/groups")
        await mkd("Api/api/groups/admin")
        await mkd("Api/api/groups/info")
        await mkd("Api/api/groups/user")
        await mkd("Api/api/login")
        await mkd("Api/api/other")
        await mkd("Api/api/plugins")
        await mkd("Api/api/plugins/info")
        await mkd("Api/api/plugins/manage")
        await mkd("Api/api/statistics")
        await mkd("Api/api/system")
        await mkd("Api/api/test")
        await download_to_api("groups/__init__")
        await download_to_api("groups/admin/__init__")
        await download_to_api("groups/info/__init__")
        await download_to_api("groups/user/__init__")
        await download_to_api("login/__init__")
        await download_to_api("other/__init__")
        await download_to_api("plugins/__init__")
        await download_to_api("plugins/info/__init__")
        await download_to_api("plugins/manage/__init__")
        await download_to_api("statistics/__init__")
        await download_to_api("system/__init__")
        await download_to_api("test/__init__")

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
