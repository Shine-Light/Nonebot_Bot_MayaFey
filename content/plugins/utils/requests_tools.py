"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 20:52
"""
import requests


# 捕获302后的网址
def match_302(url: str) -> str:
    r = requests.head(url, stream=True)
    url = r.headers['Location']
    return url

