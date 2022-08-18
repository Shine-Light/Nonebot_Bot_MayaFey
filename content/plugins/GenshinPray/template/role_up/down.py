"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/8/17 22:16
"""
import requests
import os

path = os.path.abspath(__file__).replace("down.py", "")
os.chdir(path)
names_role = open("img/avatar/name.txt", "r", encoding="utf-8").read().strip().split("\n")
names_ele = open("img/ele/name.txt", "r", encoding="utf-8").read().strip().split("\n")

for name in names_role:
    with open(f"img/avatar/{name}", "wb+") as img:
        img.write(requests.get(url=f"http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/avatar/{name}").content)

for name in names_ele:
    with open(f"img/ele/{name}", "wb+") as img:
        img.write(requests.get(url=f"http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/ele/{name}").content)
