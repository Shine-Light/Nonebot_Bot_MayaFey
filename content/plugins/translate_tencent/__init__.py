"""
Author       : Lancercmd
Date         : 2022-01-08 23:52:07
LastEditors  : Lancercmd
LastEditTime : 2022-01-08 23:52:07
Description  : None
GitHub       : https://github.com/Lancercmd
"""
from . import translator
from nonebot.plugin import PluginMetadata
from utils.other import add_target


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="translate_tencent",
    description="翻译(腾讯接口版本)",
    usage="/腾讯翻译" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "Lancercmd",
        "translate": "腾讯翻译",
    }
)