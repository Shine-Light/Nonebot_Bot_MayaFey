"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/21 12:57
"""
import os


import requests
import platform


from utils import path, other, htmlrender, json_tools, url
from pathlib import Path


async def get_update_log():
    url_log = f"http://cdn.shinelight.xyz/nonebot/version/{await get_version_last()}/log.md"
    log_md = requests.get(url_log).text
    img = await htmlrender.md_to_pic(log_md)
    return img


async def check_update() -> bool:
    version = get_version()
    version_last = await get_version_last()
    if version_last != version:
        return True
    else:
        return False


async def get_version_last() -> str:
    return requests.get(url.version_html).text


def get_version() -> str:
    return open(path.version_path, "r", encoding="utf-8").read()


async def update(gid: str) -> str:
    js = json_tools.json_load(path.updating_path)
    js['updating'] = True
    js['gid'] = gid
    json_tools.json_write(path.updating_path, js)
    version_old = get_version()
    version = str(await get_version_last())
    update_url = f"http://cdn.shinelight.xyz/nonebot/version/{version}/update.py"
    update_py_path = path.update_path / "version" / version
    if not Path.exists(update_py_path):
        await other.mk("dir", update_py_path, mode=None)
    await other.mk("file", update_py_path / "update.py", "w", url=update_url, dec="更新程序")
    dir_path = '"' + os.path.dirname(os.path.abspath(__file__))
    dir_path = dir_path.replace("\\", "/")
    dir_path += f'/version/{version}/update.py"'
    if platform.system() == "Windows":
        os.system(f"python {dir_path}")
    else:
        os.system(f"python3 {dir_path}")
    return version_old
