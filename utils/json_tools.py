"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:30
"""
import ujson as json
from pathlib import Path


# 读取json文件
def json_load(url: Path) -> dict:
    """
    读取json文件
    url: 文件路径
    返回dict对象
    """
    return json.loads(open(url, 'r', encoding='utf-8').read())


# 写入json文件
def json_write(url: Path, jsons: dict):
    """
    写入json文件
    url: 文件路径
    jsons: dict对象
    """
    with open(url, 'w', encoding='utf-8') as file:
        file.write(json.dumps(jsons, ensure_ascii=False, indent=4))


# 更新json文件
def json_update(url: Path, key, value):
    """
    更新json文件
    url: 文件路径
    key: 键
    value: 值
    """
    js = json_load(url)
    js.update({key: value})
    json_write(url, js)
