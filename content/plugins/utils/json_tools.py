"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:30
"""
import json
from pathlib import Path


# 读取json文件
def json_load(url: Path) -> dict:
    return json.loads(open(url, 'r', encoding='utf-8').read())


# 写入json文件
def json_write(url: Path, jsons: dict):
    with open(url, 'w', encoding='utf-8') as file:
        file.write(json.dumps(jsons, ensure_ascii=False))
