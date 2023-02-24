"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/8/17 22:16
"""
import aiohttp
import asyncio
import os

path = os.path.abspath(__file__).replace("down.py", "")
os.chdir(path)
names_role = open("img/avatar/name.txt", "r", encoding="utf-8").read().strip().split("\n")
# names_ele = open("img/ele/name.txt", "r", encoding="utf-8").read().strip().split("\n")
url_base = "http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/avatar/"


async def download(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url)
        return await resp.read()


async def save(name_now):
    content = await download(url_base + name_now)
    with open(f"img/avatar/{name_now}", "wb+") as img:
        img.write(content)


tasks = []
for name in names_role:
    tasks.append(save(name))
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

# for name in names_ele:
#     with open(f"img/ele/{name}", "wb+") as img:
#         img.write(requests.get(url=f"http://cdn.shinelight.xyz/nonebot/resource/GenshinPray/role_up/ele/{name}").content)
