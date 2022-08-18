import requests
import os

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/50.0.2661.87 Safari/537.36"}

path = os.path.abspath(__file__).replace("down.py", "")
os.chdir(path)
links = open("in_img.txt", "r", encoding="utf-8")
name = open("in_name.txt", "r", encoding="utf-8").read().split("\n")
a = 0

for link in links:
    with open(f"../img/{name[a]}.png", "wb+") as img:
        img.write(requests.get(url=link, headers=headers).content)
    a += 1
