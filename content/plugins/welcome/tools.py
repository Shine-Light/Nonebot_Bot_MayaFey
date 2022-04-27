"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 13:23
"""
import os

from ..utils.path import *
from ..utils.other import mk


async def init(gid: str):
    welcome_txt = welcome_path_base / f"{gid}.txt"
    back_txt = back_path_base / f"{gid}.txt"

    if not os.path.exists(welcome_txt):
        await mk("file", welcome_txt, "w", content="欢迎入群")
    if not os.path.exists(back_txt):
        await mk("file", back_txt, "w", content="欢迎回归")


async def update(content: str, gid: str, mode: str):
    if mode == 'welcome':
        welcome_txt = welcome_path_base / f"{gid}.txt"
        with open(welcome_txt, 'w', encoding="utf-8") as file:
            file.write(content)
            file.close()
    elif mode == 'back':
        back_txt = back_path_base / f"{gid}.txt"
        with open(back_txt, 'w', encoding="utf-8") as file:
            file.write(content)
            file.close()
