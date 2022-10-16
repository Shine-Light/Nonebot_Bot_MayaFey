from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, GROUP, Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.log import logger
from .utils import eating_manager, Meals, config
from nonebot import require, get_bot
from ..permission.tools import special_per, get_special_per
from utils import users

from utils.other import add_target, translate
from nonebot.plugin import PluginMetadata


message_what2eat = '''
吃什么:/{时间段}吃什么
查看群特色菜单: /群特色菜单
添加菜品至群特色菜单:/添加 {菜名} (超级用户)
从菜单移除菜品:/移除 {菜名} (超级用户)
添加菜品至基础菜单: /加菜 {菜名} (超级用户) 
查看基础菜单: /基础菜菜单 (超级用户)
开启/关闭按时饭点小助手: /开启|关闭小助手 (超级用户)
添加问候: /添加问候 {问候语} (超级用户)
删除问候: /删除问候 {问候语} (超级用户)'''.strip() + add_target(60)


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "what2eat"),
    description="今天吃什么",
    usage=message_what2eat
)

greating_helper = require("nonebot_plugin_apscheduler").scheduler
eating_helper = require("nonebot_plugin_apscheduler").scheduler


what2eat = on_regex(r"^/(今天|[早中午晚][上饭餐午]|早上|夜宵|今晚|晚上|早餐|午餐|晚餐)吃(什么|啥|点啥)", permission=GROUP, priority=9, block=False)
add_group_food = on_command("添加", priority=9, block=False)
remove_food = on_command("移除", priority=9, block=False)
add_basic = on_command("加菜", priority=9, block=False)
show_group = on_command("群特色菜单", permission=GROUP, priority=9, block=False)
show_basic = on_command("基础菜菜单", priority=9, block=False)

switch_greating = on_regex(r"/(开启|关闭)饭点小助手", priority=9, block=False)
add_greating = on_command("添加问候", aliases={"添加问候语"}, priority=9, block=False)
remove_greating = on_command("删除问候", aliases={"删除问候语"}, priority=9, block=False)


@what2eat.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = eating_manager.get2eat(event)
    await what2eat.finish(msg)

@add_group_food.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "add_group_food", str(event.group_id)):
        args = args.extract_plain_text().strip().split()
        if not args:
            await add_group_food.finish("还没输入你要添加的菜品呢~")
        elif args and len(args) == 1:
            new_food = args[0]
        else:
            await add_group_food.finish("添加菜品参数错误~")

        user_id = str(event.user_id)
        logger.info(f"User {user_id} 添加了 {new_food} 至菜单")
        msg = eating_manager.add_group_food(new_food, event)

        await add_group_food.finish(msg)
    else:
        await add_group_food.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'add_group_food')} 及以上")

@add_basic.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "add_basic", str(event.group_id)):
        args = args.extract_plain_text().strip().split()
        if not args:
            await add_basic.finish("还没输入你要添加的菜品呢~")
        elif args and len(args) == 1:
            new_food = args[0]
        else:
            await add_basic.finish("添加菜品参数错误~")

        user_id = str(event.user_id)
        logger.info(f"Superuser {user_id} 添加了 {new_food} 至基础菜单")
        msg = eating_manager.add_basic_food(new_food)

        await add_basic.finish(msg)
    else:
        await add_basic.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'add_basic')} 及以上")

@remove_food.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "remove_food", str(event.group_id)):
        args = args.extract_plain_text().strip().split()
        if not args:
            await remove_food.finish("还没输入你要移除的菜品呢~")
        elif args and len(args) == 1:
            food_to_remove = args[0]
        else:
            await remove_food.finish("移除菜品参数错误~")

        user_id = str(event.user_id)
        logger.info(f"User {user_id} 从菜单移除了 {food_to_remove}")
        msg = eating_manager.remove_food(food_to_remove, event)

        await remove_food.finish(msg)
    else:
        await remove_food.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'remove_food')} 及以上")
@show_group.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = eating_manager.show_group_menu(event)
    await show_group.finish(msg)

@show_basic.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "show_basic", str(event.group_id)):
        msg = eating_manager.show_basic_menu()
        await show_basic.finish(msg)
    else:
        await show_basic.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'show_basic')} 及以上")

@switch_greating.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "switch_greating", str(event.group_id)):
        args = event.get_plaintext()
        if args[:3] == "/开启":
            greating_helper.resume()
            msg = f"已开启按时吃饭小助手~"
        elif args[:3] == "/关闭":
            greating_helper.pause()
            msg = f"已关闭按时吃饭小助手~"

        await switch_greating.finish(msg)
    else:
        await switch_greating.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'switch_greating')} 及以上")

@add_greating.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "add_greating", str(event.group_id)):
        args = args.extract_plain_text().strip().split()
        if not args:
            await add_basic.finish("还没输入你要添加的问候语~")
        elif args and len(args) == 1:
            await add_greating.finish("输入参数数目错误~")
        elif len(args) > 2:
            await add_greating.finish("参数太多啦~")

        msg = eating_manager.add_greating(args)
        await add_greating.finish(msg)
    else:
        await add_greating.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'add_greating')} 及以上")

@remove_greating.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "remove_greating", str(event.group_id)):
        args = args.extract_plain_text().strip().split()
        if not args:
            await add_basic.finish("请输入删除问候语的类别~")
        elif args and len(args) > 1:
            await add_greating.finish("参数太多啦~")

        msg = eating_manager.remove_greating(args[0])
        await remove_greating.finish(msg)
    else:
        await remove_greating.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'remove_greating')} 及以上")

# 重置吃什么次数，包括夜宵
@eating_helper.scheduled_job("cron", hour="6,11,17,22", minute=0)
async def _():
    eating_manager.reset_eating()
    logger.info("今天吃什么次数已刷新")

# 早餐提醒
@greating_helper.scheduled_job("cron", hour=7, minute=0)
async def time_for_breakfast():
    bot = get_bot()
    msg = eating_manager.get2greating(Meals.BREAKFAST)
    if msg and len(config.groups_id) > 0:
        for group_id in config.groups_id:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        
        logger.info(f"已群发早餐提醒")

# 午餐提醒
@greating_helper.scheduled_job("cron", hour=12, minute=0)
async def time_for_lunch():
    bot = get_bot()
    msg = eating_manager.get2greating(Meals.LUNCH)
    if msg and len(config.groups_id) > 0:
        for group_id in config.groups_id:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        
        logger.info(f"已群发午餐提醒")

# 下午茶/摸鱼提醒
@greating_helper.scheduled_job("cron", hour=15, minute=0)
async def time_for_snack():
    bot = get_bot()
    msg = eating_manager.get2greating(Meals.SNACK)
    if msg and len(config.groups_id) > 0:
        for group_id in config.groups_id:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        
        logger.info(f"已群发摸鱼提醒")

# 晚餐提醒
@greating_helper.scheduled_job("cron", hour=18, minute=0)
async def time_for_dinner():
    bot = get_bot()
    msg = eating_manager.get2greating(Meals.DINNER)
    if msg and len(config.groups_id) > 0:
        for group_id in config.groups_id:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        
        logger.info(f"已群发晚餐提醒")

# 夜宵提醒
@greating_helper.scheduled_job("cron", hour=22, minute=0)
async def time_for_midnight():
    bot = get_bot()
    msg = eating_manager.get2greating(Meals.MIDNIGHT)
    if msg and len(config.groups_id) > 0:
        for group_id in config.groups_id:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        
        logger.info(f"已群发夜宵提醒")