"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:30
"""
import aiofiles
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


# 删除属性
def json_pop(url: Path, key):
    """
    删除属性
    url: 文件路径
    key: 键
    """
    js = json_load(url)
    js.pop(key)
    json_write(url, js)


# 读取json文件
async def json_load_async(url: Path) -> dict:
    """
    异步读取json文件
    url: 文件路径
    返回dict对象
    """
    async with aiofiles.open(url, 'r', encoding='utf-8') as file:
        return json.loads(await file.read())


# 写入json文件
async def json_write_async(url: Path, jsons: dict):
    """
    异步写入json文件
    url: 文件路径
    jsons: dict对象
    """
    async with aiofiles.open(url, 'w', encoding='utf-8') as file:
        await file.write(json.dumps(jsons, ensure_ascii=False, indent=4))


# 更新json文件
async def json_update_async(url: Path, key, value):
    """
    异步更新json文件
    url: 文件路径
    key: 键
    value: 值
    """
    js = await json_load_async(url)
    js.update({key: value})
    await json_write_async(url, js)


# 删除属性
async def json_pop_async(url: Path, key):
    """
    删除属性
    url: 文件路径
    key: 键
    """
    js = await json_load_async(url)
    js.pop(key)
    await json_write_async(url, js)
