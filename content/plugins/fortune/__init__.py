from nonebot import logger, on_command, on_regex, on_fullmatch, require
from nonebot.params import Depends, CommandArg, RegexMatched
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GROUP, Message, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from nonebot.plugin import PluginMetadata
from .config import MainThemeList
from utils.other import add_target, translate
from utils import users
from utils.permission import special_per, get_special_per

__fortune_version__ = "v0.4.5"
__fortune_notes__ = f'''
今日运势 {__fortune_version__}
抽签: /今日运势
指定主题抽签: xx抽签    
查看可选的抽签主题: /主题列表 
指定特殊角色签底: 指定xx签 (需要自己尝试哦~)
设置群抽签主题: 设置xx签 (超级用户)
重置群抽签主题: /重置主题 (超级用户)
查看群抽签主题: /查看主题
刷新抽签: /刷新抽签 (超级用户)'''.strip() + add_target(60)

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "fortune"),
    description="抽取你的今日运势",
    usage=__fortune_notes__
)

divine = on_command("今日运势", aliases={"抽签", "运势"}, permission=GROUP, priority=8, block=False)
limit_setting = on_regex(r"指定(.*?)签", permission=GROUP, priority=8, block=False)
theme_setting = on_regex(r"设置(.*?)签", permission=GROUP, priority=8, block=False)
fortune_reset = on_command("重置抽签", permission=GROUP, priority=8, block=False)
theme_list = on_command("主题列表", permission=GROUP, priority=8, block=False)
show = on_command("抽签设置", permission=GROUP, priority=8, block=False)
divine_specific = on_regex(r"^.+抽签$", permission=GROUP, priority=8)
reset = on_regex("^重置(抽签)?主题$", permission=GROUP, priority=8, block=False)
fortune_refresh = on_fullmatch("/刷新抽签", priority=8, block=False)


@show.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    theme = fortune_manager.get_setting(gid)
    show_theme = MainThemeList[theme][0]
    await show.finish(f"当前群抽签主题：{show_theme}")


@theme_list.handle()
async def _(matcher: Matcher):
    msg = fortune_manager.get_main_theme_list()
    await matcher.finish(msg)


@divine.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text()

    if "帮助" in args[-2:]:
        await divine.finish(__fortune_notes__)

    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = event.sender.card if event.sender.card else event.sender.nickname

    image_file, status = fortune_manager.divine(None, None, gid, uid, nickname)
    if image_file is False:
        await divine.finish("今日运势生成出错……")

    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await divine.finish(msg, at_sender=True)


async def get_user_theme(matcher: Matcher, state: T_State, args: str = RegexMatched()):
    arg = args[:-2]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return {**state, "user_theme": arg}


@divine_specific.handle()
async def _(event: GroupMessageEvent, state: T_State = Depends(get_user_theme)):
    user_theme = state["user_theme"]
    if "刷新" in user_theme or "重置" in user_theme:
        return
    for theme in MainThemeList:
        if user_theme in MainThemeList[theme]:
            if not fortune_manager.theme_enable_check(theme):
                await divine_specific.finish("该抽签主题未启用~")
            else:
                gid = str(event.group_id)
                uid = str(event.user_id)
                nickname = event.sender.card if event.sender.card else event.sender.nickname

                image_file, status = fortune_manager.divine(theme, None, gid, uid, nickname)
                if image_file is False:
                    await divine_specific.finish("今日运势生成出错……")

                if not status:
                    msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
                else:
                    logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
                    msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

            await divine_specific.finish(msg, at_sender=True)

    await divine_specific.finish("还没有这种抽签主题哦~")


async def get_user_arg(matcher: Matcher, state: T_State, args: str = RegexMatched()):
    arg = args[2:-1]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return {**state, "user_arg": arg}


@theme_setting.handle()
async def _(event: GroupMessageEvent, state: T_State = Depends(get_user_arg)):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "theme_setting", str(event.group_id)):
        user_theme = state["user_arg"]
        gid = str(event.group_id)

        for theme in MainThemeList:
            if user_theme in MainThemeList[theme]:
                if not fortune_manager.divination_setting(theme, gid):
                    await theme_setting.finish("该抽签主题未启用~")
                else:
                    await theme_setting.finish("已设置当前群抽签主题~")

        await theme_setting.finish("还没有这种抽签主题哦~")
    else:
        await theme_setting.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'theme_setting')} 及以上")


@limit_setting.handle()
async def _(event: GroupMessageEvent, state: T_State = Depends(get_user_arg)):
    '''
        指定签底抽签功能将在v0.5.x版本中弃用，但会保留在v0.4.x，届时请查看README说明
    '''
    logger.warning(
        "The command of divining by indicating the basic image of a specific theme will be deprecated in version v0.5.x in the future, but will be reserved in v0.4.x")

    limit = state["user_arg"]
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = event.sender.card if event.sender.card else event.sender.nickname

    if limit == "随机":
        image_file, status = fortune_manager.divine(None, None, gid, uid, nickname)
        if image_file is False:
            await limit_setting.finish("今日运势生成出错……")
    else:
        spec_path = fortune_manager.limit_setting_check(limit)
        if not spec_path:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
        else:
            image_file, status = fortune_manager.divine(None, spec_path, gid, uid, nickname)
            if image_file is False:
                await limit_setting.finish("今日运势生成出错……")

    if not status:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦🤗\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await limit_setting.finish(msg, at_sender=True)


@fortune_reset.handle()
async def _(event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "fortune_reset", str(event.group_id)):
        gid = str(event.group_id)
        fortune_manager.divination_setting("random", gid)
        await fortune_reset.finish("已重置当前群抽签主题为随机~")
    else:
        await fortune_reset.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'fortune_reset')} 及以上")


@fortune_refresh.handle()
async def _(event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "fortune_refresh", str(event.group_id)):
        fortune_manager.reset_fortune()
        await limit_setting.finish("今日运势已刷新!")
    else:
        await fortune_refresh.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'fortune_refresh')} 及以上")


# 重置每日占卜
scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")
