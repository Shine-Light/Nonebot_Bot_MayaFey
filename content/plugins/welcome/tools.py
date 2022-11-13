"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/28 13:23
"""
from utils.path import *


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
