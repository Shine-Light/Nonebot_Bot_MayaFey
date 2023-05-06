from nonebot import require
from nonebot import logger
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GROUP, Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from .data_source import morning_manager

from utils.matcherManager import matcherManager
from utils import users
from utils.other import add_target


message_morning: str = '''
早安: /早安|哦嗨哟|おはよう
晚安: /晚安|哦呀斯密|おやすみ
查看自己的作息: /我的作息
查看群友的作息: /群友作息
查看配置: /早晚安设置

=== 设置(超级用户) ===
开启某个配置: /早安开启 xx 
关闭某个配置: /早安关闭 xx 
设置数值: /早安设置 {配置} {数值}
开启某个配置: /晚安开启 xx 
关闭某个配置: /晚安关闭 xx 
设置数值: /晚安设置 {配置} {数值} '''.strip() + add_target(60)


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="morning",
    description="早晚安记录作息，培养优质睡眠😴",
    usage=message_morning,
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "permission_special": {
            "morning:morning_setting": "superuser",
            "morning:morning_on": "superuser",
            "morning:morning_off": "superuser",
            "morning:night_setting": "superuser",
            "morning:night_on": "superuser",
            "morning:night_off": "superuser",
        },
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "KafCoppelia",
    }
)


morning = on_command("早安", aliases={"哦嗨哟", "おはよう"}, permission=GROUP, priority=8, block=False)
night = on_command("晚安", aliases={"哦呀斯密", "おやすみ"}, permission=GROUP, priority=8, block=False)
# routine
my_routine = on_command("我的作息", permission=GROUP, priority=8, block=False)
fellow_routine = on_command("群友作息", permission=GROUP, priority=8, block=False)
# setting
setting = on_command("早晚安设置", permission=GROUP, priority=8, block=False)
morning_setting = on_command("早安设置", permission=GROUP, priority=8, block=False)
morning_on = on_command("早安开启", permission=GROUP, priority=8, block=False)
morning_off = on_command("早安关闭", permission=GROUP, priority=8, block=False)
night_setting = on_command("晚安设置", permission=GROUP, priority=8, block=False)
night_on = on_command("晚安开启", permission=GROUP, priority=8, block=False)
night_off = on_command("晚安关闭", permission=GROUP, priority=8, block=False)

matcherManager.addMatcher("morning:morning_setting", morning_setting)
matcherManager.addMatcher("morning:morning_on", morning_on)
matcherManager.addMatcher("morning:morning_off", morning_off)
matcherManager.addMatcher("morning:night_setting", night_setting)
matcherManager.addMatcher("morning:night_on", night_on)
matcherManager.addMatcher("morning:night_off", night_off)

scheduler = require("nonebot_plugin_apscheduler").scheduler


@morning.handle()
async def good_morning(bot: Bot, event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    mem_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    sex = mem_info['sex']
    if sex == 'male':
        sex_str = '少年'
    elif sex == 'female':
        sex_str = '少女'
    else:
        sex_str = '群友'

    msg = morning_manager.get_morning_msg(sex_str, event)
    await morning.finish(message=msg, at_sender=True)

@night.handle()
async def good_night(bot: Bot, event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    mem_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    sex = mem_info['sex']
    if sex == 'male':
        sex_str = '少年'
    elif sex == 'female':
        sex_str = '少女'
    else:
        sex_str = '群友'

    msg = morning_manager.get_night_msg(sex_str, event)
    await night.finish(message=msg, at_sender=True)

@my_routine.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = morning_manager.get_routine(event)
    await my_routine.finish(message=msg, at_sender=True)

@fellow_routine.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = morning_manager.get_group_routine(event)
    await fellow_routine.finish(msg)

@setting.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = morning_manager.get_current_config()
    await setting.finish(msg)

@morning_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await morning_setting.finish("还没输入参数呢~")
    elif args and len(args) > 3:
        await morning_on.finish("参数太多啦~")
    msg = morning_manager.morning_config(args)
    await morning_setting.finish(msg)

@morning_on.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await morning_on.finish("还没输入参数呢~")
    elif args and len(args) == 1:
        msg = morning_manager.morning_switch(args[0], True)
    else:
        await morning_on.finish("参数太多啦~")
    await morning_on.finish(msg)

@morning_off.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await morning_off.finish("还没输入参数呢~")
    elif args and len(args) == 1:
        msg = morning_manager.morning_switch(args[0], False)
    else:
        await morning_off.finish("参数太多啦~")
    await morning_off.finish(msg)

@night_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await night_setting.finish("还没输入参数呢~")
    elif args and len(args) > 3:
        await morning_on.finish("参数太多啦~")

    msg = morning_manager.night_config(args)
    await night_setting.finish(msg)

@night_on.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await night_on.finish("还没输入参数呢~")
    elif args and len(args) == 1:
        msg = morning_manager.night_switch(args[0], True)
    else:
        await night_on.finish("参数太多啦~")
    await night_on.finish(msg)

@night_off.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().strip().split()
    if not args:
        await night_off.finish("还没输入参数呢~")
    elif args and len(args) == 1:
        msg = morning_manager.night_switch(args[0], False)
    else:
        await night_off.finish("参数太多啦~")
    await night_off.finish(msg)

# 重置一天的早安晚安计数
@scheduler.scheduled_job("cron", hour=0, minute=0)
async def _():
    morning_manager.reset_data()
    logger.info("早晚安已刷新！")
