import aiohttp
import asyncio
import os

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/50.0.2661.87 Safari/537.36"}

path = os.path.abspath(__file__).replace("down.py", "")
os.chdir(path)
links = open("in_img.txt", "r", encoding="utf-8")
name = open("in_name.txt", "r", encoding="utf-8").read().split("\n")
a = 0


async def download(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url, headers=headers)
        return await resp.read()


async def save(url, name_now):
    content = await download(url)
    with open(f"../img/{name_now}.png", "wb+") as img:
        img.write(content)


tasks = []
for link in links:
    tasks.append(save(link, name[a]))
    a += 1
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
