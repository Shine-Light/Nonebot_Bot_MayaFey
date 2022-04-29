"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/21 12:57
"""
import os
import sys


import requests
import platform


from ..utils import path, other, htmlrender, json_tools
from pathlib import Path


async def get_update_log():
    url = f"http://cdn.shinelight.xyz/nonebot/version/{await get_version_last()}/log.md"
    log_md = requests.get(url).text
    img = await htmlrender.md_to_pic(log_md)
    return img


async def check_update() -> bool:
    version = await get_version()
    version_last = await get_version_last()
    if version_last > version:
        return True
    else:
        return False


async def get_version_last() -> float:
    return float(requests.get("http://cdn.shinelight.xyz/nonebot/version.html").text)


async def get_version() -> float:
    return float(os.listdir(path.update_path / "version")[0])


async def update(gid: str) -> float:
    js = json_tools.json_load(path.updating_path)
    js['updating'] = True
    js['gid'] = gid
    json_tools.json_write(path.updating_path, js)
    version_old = await get_version()
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


async def reboot():
    if platform.system() == "Windows":
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        os.execv(sys.executable, ['python3'] + sys.argv)
