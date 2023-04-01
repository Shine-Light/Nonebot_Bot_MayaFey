from nonebot import on_command, on_regex, on_fullmatch
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, CommandArg, RegexGroup
from nonebot.matcher import Matcher
from nonebot import require, get_driver
from nonebot.adapters.onebot.v11 import GROUP, Message, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from .config import FortuneThemesDict
from utils.other import add_target
from utils.matcherManager import matcherManager

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

command_start = "".join(get_driver().config.command_start)
__fortune_version__ = "v0.4.10.post1"
__fortune_usages__ = f'''
[今日运势/抽签/运势] 一般抽签
[xx抽签]     指定主题抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置主题] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[查看主题] 查看群抽签主题'''.strip() + add_target(60)

__plugin_meta__ = PluginMetadata(
    name="fortune",
    description="抽签！占卜你的今日运势🙏",
    usage=__fortune_usages__,
    extra={
        "author": "KafCoppelia <k740677208@gmail.com>",
        "version": __fortune_version__,
        "permission_common": "member",
        "permission_special": {
            "fortune:change_theme": "superuser",
            "fortune:reset_themes": "superuser"
        },
        "unset": False,
        "total_unable": False,
        "translate": "今日运势"
    }
)

general_divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8, block=False)
specific_divine = on_regex(rf"^[{command_start}]?(.*?)抽签$", permission=GROUP, priority=8, block=False)
limit_setting = on_regex(rf"^[{command_start}]?指定(.*?)签$", permission=GROUP, priority=8, block=False)
change_theme = on_regex(rf"^[{command_start}]?设置(.*?)签$", permission=GROUP, priority=8, block=False)
reset_themes = on_regex(rf"^[{command_start}]?重置(抽签)?主题$", permission=GROUP, priority=8, block=False)
themes_list = on_command("主题列表", permission=GROUP, priority=8, block=False)
show_themes = on_regex(rf"^[{command_start}]?查看(抽签)?主题$", permission=GROUP, priority=8)
matcherManager.addMatcher("fortune:change_theme", change_theme)
matcherManager.addMatcher("fortune:reset_themes", reset_themes)


@show_themes.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    theme: str = fortune_manager.get_group_theme(gid)
    await show_themes.finish(f"当前群抽签主题：{FortuneThemesDict[theme][0]}")


@themes_list.handle()
async def _(event: GroupMessageEvent):
    msg: str = fortune_manager.get_available_themes()
    await themes_list.finish(msg)


@general_divine.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg: str = args.extract_plain_text()

    if "帮助" in arg[-2:]:
        await general_divine.finish(__fortune_usages__)

    gid: str = str(event.group_id)
    uid: str = str(event.user_id)

    is_first, image_file = fortune_manager.divine(gid, uid, None, None)
    if image_file is None:
        await general_divine.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await general_divine.finish(msg, at_sender=True)


async def get_user_theme(matcher: Matcher, args: tuple = RegexGroup()) -> str:
    arg: str = args[0]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return arg


@specific_divine.handle()
async def _(event: GroupMessageEvent, user_theme: str = Depends(get_user_theme)):
    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not fortune_manager.theme_enable_check(theme):
                await specific_divine.finish("该抽签主题未启用~")
            else:
                gid: str = str(event.group_id)
                uid: str = str(event.user_id)

                is_first, image_file = fortune_manager.divine(
                    gid, uid, theme, None)
                if image_file is None:
                    await specific_divine.finish("今日运势生成出错……")

                if not is_first:
                    msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
                else:
                    logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
                    msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

            await specific_divine.finish(msg, at_sender=True)

    await specific_divine.finish("还没有这种抽签主题哦~")


async def get_user_arg(matcher: Matcher, args: tuple = RegexGroup()) -> str:
    arg: str = args[0]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return arg


@change_theme.handle()
async def _(event: GroupMessageEvent, user_theme: str = Depends(get_user_arg)):
    gid: str = str(event.group_id)

    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not fortune_manager.divination_setting(theme, gid):
                await change_theme.finish("该抽签主题未启用~")
            else:
                await change_theme.finish("已设置当前群抽签主题~")

    await change_theme.finish("还没有这种抽签主题哦~")


@limit_setting.handle()
async def _(event: GroupMessageEvent, limit: str = Depends(get_user_arg)):
    logger.warning("指定签底抽签功能将在 v0.5.x 弃用")

    gid: str = str(event.group_id)
    uid: str = str(event.user_id)

    if limit == "随机":
        is_first, image_file = fortune_manager.divine(gid, uid, None, None)
        if image_file is None:
            await limit_setting.finish("今日运势生成出错……")
    else:
        spec_path = fortune_manager.specific_check(limit)
        if not spec_path:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
        else:
            is_first, image_file = fortune_manager.divine(gid, uid, None, spec_path)
            if image_file is None:
                await limit_setting.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {uid} | Group {gid} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await limit_setting.finish(msg, at_sender=True)


@reset_themes.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    if not fortune_manager.divination_setting("random", gid):
        await reset_themes.finish("重置群抽签主题失败！")

    await reset_themes.finish("已重置当前群抽签主题为随机~")


# 清空昨日生成的图片
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    fortune_manager.clean_out_pics()
    logger.info("昨日运势图片已清空！")
