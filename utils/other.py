"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 18:32
"""
import os
import platform
import sys

import httpx

from nonebot import logger


async def mk(type_, path_, *mode, **kwargs):
    """
    创建文件夹 下载文件
    :param type_: ['dir', 'file']
    :param path_: Path
    :param mode: ['wb', 'w']
    :param kwargs: ['url', 'content', 'dec', 'info'] 文件地址 写入内容 描述信息 和 额外信息
    :return: None
    """
    if 'info' in kwargs:
        logger.info(kwargs['info'])
    if type_ == "dir":
        os.mkdir(path_)
        logger.info(f"创建文件夹{path_}")
    elif type_ == "file":
        if 'url' in kwargs:
            if kwargs['dec']:
                logger.info(f"开始下载文件{kwargs['dec']}")
            async with httpx.AsyncClient() as client:
                r = await client.get(kwargs['url'])
                if mode[0] == "w":
                    with open(path_, "w", encoding="utf-8") as f:
                        f.write(r.text)
                elif mode[0] == "wb":
                    with open(path_, "wb") as f:
                        f.write(r.content)
                logger.info(f"下载文件 {kwargs['dec']} 到 {path_}")
        else:
            if mode:
                with open(path_, mode[0], encoding="utf-8") as f:
                    f.write(kwargs["content"])
                logger.info(f"创建文件{path_}")
            else:
                raise Exception("mode 不能为空")
    else:
        raise Exception("type_参数错误")


async def reboot():
    if platform.system() == "Windows":
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        os.execv(sys.executable, ['python3'] + sys.argv)
