"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 22:30
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from utils import database_mysql
from . import tools

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "credit"),
    description="积分查询和排行",
    usage="/积分排行\n"
          "/我的积分" + add_target(60)
)


cursor = database_mysql.cursor
db = database_mysql.connect





# 积分排行榜
top = on_command(cmd="积分排行", aliases={"积分排名", "积分排行榜", "积分前十", "积分前10"}, priority=8)
@top.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message = await tools.top(str(event.group_id), bot)
    await top.send(message=message[:-1] + add_target(60))


# 查看自己的积分
num = on_command(cmd="积分", aliases={"我的积分", "积分数", "credit"}, priority=8)
@num.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    credit = await tools.get(str(event.group_id), str(event.user_id))
    await top.send(message=f"你的积分为:{credit}", at_sender=True)
