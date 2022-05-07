"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 20:52
"""
import requests
from nonebot import get_driver


proxy = get_driver().config.proxy


# 捕获302后的网址
def match_302(url: str) -> str:
    r = requests.head(url, stream=True)
    url = r.headers['Location']
    return url


def get_proxy():
    print(str.replace(proxy, "x", ""))
    if proxy and str.replace(proxy, "x", "") != "":
        proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy
        }
        return proxies
    return None
