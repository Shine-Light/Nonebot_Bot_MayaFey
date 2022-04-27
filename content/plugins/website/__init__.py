"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 19:51
"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from ..withdraw import add_target


# 夹带私货
message = '''开发的个人主页:https://shinelight.xyz
群主的博客:https://yangyang5418.github.io'''

website = on_command(cmd="网站", aliases={"website", "个人网站"}, priority=8)
@website.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await website.send(message=message + add_target(30))
