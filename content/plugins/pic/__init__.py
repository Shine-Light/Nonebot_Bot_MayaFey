"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 18:29
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from utils import requests_tools

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "pic"),
    description="随机一张图片",
    usage="/随机图片 头像|Bing|二次元图片" + add_target(60)
)


url: str = "https://api.yimian.xyz/img?"


pic = on_command(cmd="随机图片", aliases={"图片"}, priority=8)
@pic.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    content: list = str(event.get_message()).split('片')
    type_pic = 'moe'
    if len(content) == 2:
        tp: str = content[1]
        if tp == 'Bing' or tp == 'Bing每日壁纸':
            type_pic = 'wallpaper'
        elif tp == '二次元头像' or tp == '头像':
            type_pic = 'head'
        else:
            pass

    try:
        await pic.send(message=MessageSegment.image(file=requests_tools.match_30X(url + "type=" + type_pic)))
    except Exception as e:
        if str(e) == "<NetWorkError message=WebSocket API call timeout>":
            await pic.send("请求超时,请等待请求完成")
        else:
            await pic.send("未知异常:" + str(e))

