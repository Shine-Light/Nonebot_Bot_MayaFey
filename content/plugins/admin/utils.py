"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/26 18:34
"""
import json
from typing import Optional
import aiofiles


async def load(path) -> Optional[dict]:
    """
    加载json文件
    :return: Optional[dict]
    """
    try:
        async with aiofiles.open(path, mode='r', encoding="utf-8") as f:
            contents_ = await f.read()
            contents = json.loads(contents_)
            await f.close()
            return contents
    except FileNotFoundError:
        return None


async def upload(path, dict_content) -> None:
    """
    更新json文件
    :param path: 路径
    :param dict_content: python对象，字典
    """
    async with aiofiles.open(path, mode='w', encoding="utf-8") as c:
        await c.write(str(json.dumps(dict_content)))
        await c.close()
