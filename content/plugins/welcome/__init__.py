"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 22:04
"""
import ujson as json

from nonebot import on_notice, on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, GroupIncreaseNoticeEvent, Event, MessageSegment
from nonebot.rule import Rule
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from . import tools
from utils.path import *
from utils import database_mysql, users
from utils.other import add_target
from utils.matcherManager import matcherManager


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="welcome",
    description="欢迎新人入群和老朋友回归",
    usage="/入群欢迎 {内容} (超级用户)\n"
          "/回群欢迎 {内容} (超级用户)" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "baned",
        "permission_special": {
            "welcome:welcome_msg_update": "superuser",
            "welcome:back_msg_update": "superuser",
        },
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "入群欢迎",
    }
)


cursor = database_mysql.cursor
db = database_mysql.connect
superusers = get_driver().config.superusers


# 入群检测
def checker():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_increase':
            return True

    return Rule(_checker)


member_in = on_notice(rule=checker(), priority=4, block=False)
@member_in.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.get_user_id() == bot.self_id:
        return
    gid = str(event.group_id)
    uid = str(event.get_user_id())
    re = await users.is_user_exist(gid, uid)
    # 入群欢迎
    welcome_txt = welcome_path_base / f"{gid}.txt"
    message: str = open(welcome_txt, 'r', encoding="utf-8").read()
    # 回归欢迎
    if re:
        back_txt = back_path_base / f"{gid}.txt"
        message: str = open(back_txt, 'r', encoding="utf-8").read()
    await member_in.send(message=Message(message), at_sender=True)


welcome_msg_update = on_command(cmd="入群欢迎", priority=7)
matcherManager.addMatcher("welcome:welcome_msg_update", welcome_msg_update)
@welcome_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args=CommandArg()):
    if args:
        matcher.set_arg("content", args)


@welcome_msg_update.got(key="content", prompt="要怎么欢迎呢")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True)).get("nickname")
    content = matcher.get_arg("content") + MessageSegment.text(f"\n由 {nickname}({uid}) 编辑")
    await tools.update(str(content), gid, "welcome")
    await back_msg_update.send("修改成功")


back_msg_update = on_command(cmd="回归欢迎", aliases={"回群欢迎"}, priority=7)
matcherManager.addMatcher("welcome:back_msg_update", back_msg_update)
@back_msg_update.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args=CommandArg()):
    if args:
        matcher.set_arg("content", args)

@back_msg_update.got(key="content", prompt="要怎么欢迎呢")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True)).get("nickname")
    content = matcher.get_arg("content") + MessageSegment.text(f"\n由 {nickname}({uid}) 编辑")
    await tools.update(str(content), gid, "back")
    await back_msg_update.send("修改成功")
