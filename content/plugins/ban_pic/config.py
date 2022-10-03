"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/1 13:56
"""
from nonebot import get_driver
from nonebot.log import logger

config = get_driver().config


class Config(object):
    try:
        access_key_baidu = config.baidu_image_key
        access_secret_baidu = config.baidu_image_secret
        check_level = config.baidu_image_level
    except:
        access_key_baidu = ""
        access_secret_baidu = ""
        check_level = 1
        logger.error("无法获取违禁图检测百度云配置,若使用腾讯接口请忽略此信息")
