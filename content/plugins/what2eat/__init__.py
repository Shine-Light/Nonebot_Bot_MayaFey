from typing import Coroutine, Any, List
from nonebot import on_command, on_regex, logger, require
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment, \
    GroupMessageEvent
from nonebot.params import Depends, Arg, ArgStr, CommandArg, RegexMatched
from nonebot.matcher import Matcher
from .utils import Meals, save_cq_image
from .data_source import eating_manager
from nonebot.plugin import PluginMetadata
from utils.other import translate, add_target, get_bot_name
from utils.permission import special_per, get_special_per
from utils import users

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

__what2eat_version__ = "v0.3.4"
__what2eat_notes__ = f'''
今天吃什么？ {__what2eat_version__}
[xx吃xx]    问 {get_bot_name()} 吃什么
[xx喝xx]    问 {get_bot_name()} 喝什么
[菜品添加 xx]   添加菜品至群菜单
[移除菜品 xx]   从菜单移除菜品
[加菜 xx]   添加菜品至基础菜单
[吃什么菜单]        查看群菜单
[吃什么基础菜单] 查看基础菜单
[开启/关闭饭点小助手] 开启/关闭饭点小助手
[添加/删除饭点问候 时段 问候语] 添加/删除饭点小助手问候语'''.strip()
# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "what2eat"),
    description="今天吃什么",
    usage=__what2eat_notes__ + add_target(60)
)

what2eat = on_regex(r"^(今天|[早中午晚][上饭餐午]|早上|夜宵|今晚)吃(什么|啥|点啥)(帮助)?$", priority=8, block=False)
what2drink = on_regex(r"^(今天|[早中午晚][上饭餐午]|早上|夜宵|今晚)喝(什么|啥|点啥)(帮助)?$", priority=8, block=False)
group_add = on_command("菜品添加", aliases={"添加菜品", "增加菜品", "菜品增加"}, priority=8, block=False)
group_remove = on_command("移除菜品", aliases={"菜品移除", "删除菜品", "菜品删除"}, priority=8, block=False)
basic_add = on_command("加菜", priority=8, block=False)
show_group_menu = on_command("吃什么菜单", aliases={"吃什么群菜单", "查看吃什么菜单"}, priority=8, block=False)
show_basic_menu = on_command("吃什么基础菜单", priority=8, block=False)

greeting_on = on_command("开启饭点小助手", aliases={"启用饭点小助手", "启用吃饭小助手", "开启吃饭小助手"}, priority=8,
                         block=False)
greeting_off = on_command("关闭饭点小助手", aliases={"禁用饭点小助手", "禁用吃饭小助手", "关闭吃饭小助手"}, priority=8,
                          block=False)
add_greeting = on_command("添加问候", aliases={"添加问候语"}, priority=8,
                          block=False)
remove_greeting = on_command("删除饭点问候", aliases={"删除饭点问候语", "移除饭点问候", "移除饭点问候语"}, priority=8, block=False)


@what2eat.handle()
async def _(event: MessageEvent, args: str = RegexMatched()):
    if args[-2:] == "帮助":
        await what2eat.finish(__what2eat_notes__)

    msg = eating_manager.get2eat(event)
    await what2eat.finish(msg)


@what2drink.handle()
async def _(event: MessageEvent, args: str = RegexMatched()):
    if args[-2:] == "帮助":
        await what2drink.finish(__what2eat_notes__)

    msg = eating_manager.get2drink(event)
    await what2drink.finish(msg)


@group_add.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "group_add", gid):
        args_str: List[str] = args.extract_plain_text().strip().split()
        if not args_str:
            await group_add.finish("还没输入你要添加的菜品呢~")
        elif len(args_str) > 1:
            await group_add.finish("添加菜品参数错误~")

        # If image included, save it, return the path in string
        await save_cq_image(args, eating_manager._img_dir)

        # Record the whole string, including the args after transfering
        msg: str = eating_manager.add_group_food(event, str(args))

        if "[CQ:image" in str(args):
            await group_add.finish(args.append(MessageSegment.text(" " + msg)))
        else:
            await group_add.finish(args.append(MessageSegment.text(msg)))
    else:
        await group_add.finish(
            f"无权限,权限需在 {get_special_per(gid, 'group_add')} 及以上")

@basic_add.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "basic_add", gid):
        args_str: List[str] = args.extract_plain_text().strip().split()
        if not args_str:
            await basic_add.finish("还没输入你要添加的菜品呢~")
        elif len(args_str) > 1:
            await group_add.finish("添加菜品参数错误~")

        # The same as above
        await save_cq_image(args, eating_manager._img_dir)
        msg: str = eating_manager.add_basic_food(str(args))

        if "[CQ:image" in str(args):
            await group_add.finish(args.append(MessageSegment.text(" " + msg)))
        else:
            await group_add.finish(args.append(MessageSegment.text(msg)))
    else:
        await basic_add.finish(
            f"无权限,权限需在 {get_special_per(gid, 'basic_add')} 及以上")


@group_remove.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "group_remove", gid):
        args: List[str] = args.extract_plain_text().strip().split()
        if not args:
            await group_remove.finish("还没输入你要移除的菜品呢~")
        elif len(args) > 1:
            await group_remove.finish("移除菜品参数错误~")

        msg: MessageSegment = eating_manager.remove_food(event, args[0])

        await group_remove.finish(MessageSegment.text(msg))
    else:
        await group_remove.finish(
            f"无权限,权限需在 {get_special_per(gid, 'group_remove')} 及以上")


@show_group_menu.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    is_too_many_lines, msg = eating_manager.show_group_menu(gid)
    if is_too_many_lines:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id,
                           messages=MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], msg))
    else:
        await matcher.finish(msg)


@show_basic_menu.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    is_too_many_lines, msg = eating_manager.show_basic_menu()
    if is_too_many_lines:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id,
                           messages=MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], msg))
    else:
        await matcher.finish(msg)


# ------------------------- Greetings -------------------------
@greeting_on.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "greeting_on", gid):
        eating_manager.update_groups_on(gid, True)
        await greeting_on.finish("已开启吃饭小助手~")
    else:
        await greeting_on.finish(
            f"无权限,权限需在 {get_special_per(gid, 'greeting_on')} 及以上")


@greeting_off.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "greeting_off", gid):
        eating_manager.update_groups_on(gid, False)
        await greeting_off.finish("已关闭吃饭小助手~")
    else:
        await greeting_off.finish(
            f"无权限,权限需在 {get_special_per(gid, 'greeting_off')} 及以上")


def parse_greeting() -> Coroutine[Any, Any, None]:
    '''
        Parser the greeting input from user then store in state["greeting"]
    '''

    async def _greeting_parser(matcher: Matcher, state: T_State, input_arg: Message = Arg("greeting")) -> None:
        if input_arg.extract_plain_text() == "取消":
            await matcher.finish("操作已取消")
        else:
            state["greeting"] = input_arg

    return _greeting_parser


def parse_meal() -> Coroutine[Any, Any, None]:
    '''
        Parser the meal input from user then store in state["meal"]. If illigal, reject it
    '''

    async def _meal_parser(matcher: Matcher, state: T_State, input_arg: str = ArgStr("meal")) -> None:
        if input_arg == "取消":
            await matcher.finish("操作已取消")

        res = eating_manager.which_meals(input_arg)
        if res is None:
            await matcher.reject_arg("meal", "输入时段不合法")
        else:
            state["meal"] = res

    return _meal_parser


def parse_index() -> None:
    '''
        Parser the index of greeting to be removed input from user then store in state["index"]
    '''

    async def _index_parser(matcher: Matcher, state: T_State, input_arg: str = ArgStr("index")) -> None:
        try:
            arg2int = int(input_arg)
        except ValueError:
            await matcher.reject_arg("index", "输入序号不合法")

        if arg2int == 0:
            await matcher.finish("操作已取消")
        else:
            state["index"] = arg2int

    return _index_parser


@add_greeting.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "add_greeting", gid):
        args = args.extract_plain_text().strip().split()
        if args and len(args) <= 2:
            res = eating_manager.which_meals(args[0])
            if isinstance(res, Meals):
                matcher.set_arg("meal", args[0])
                if len(args) == 2:
                    matcher.set_arg("greeting", args[1])
    else:
        await add_greeting.finish(
            f"无权限,权限需在 {get_special_per(gid, 'add_greeting')} 及以上")


@remove_greeting.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "remove_greeting", gid):
        args = args.extract_plain_text().strip().split()
        if args:
            res = eating_manager.which_meals(args[0])
            if isinstance(res, Meals):
                matcher.set_arg("meal", args[0])
    else:
        await remove_greeting.finish(
            f"无权限,权限需在 {get_special_per(gid, 'remove_greeting')} 及以上")


@add_greeting.got(
    "meal",
    prompt="请输入添加问候语的时段，可选：早餐/午餐/摸鱼/晚餐/夜宵，输入取消以取消操作",
    parameterless=[Depends(parse_meal())]
)
async def handle_skip():
    add_greeting.skip()


@add_greeting.got(
    "greeting",
    prompt="请输入添加的问候语，输入取消以取消操作",
    parameterless=[Depends(parse_greeting())]
)
async def handle_add_greeting(state: T_State, greeting: Message = Arg()):
    meal = state["meal"]
    # Not support for text + image greeting, just extract the plain text
    msg = eating_manager.add_greeting(meal, greeting.extract_plain_text())
    await add_greeting.finish(msg)


@remove_greeting.got(
    "meal",
    prompt="请输入删除问候语的时段，可选：早餐/午餐/摸鱼/晚餐/夜宵，输入取消以取消操作",
    parameterless=[Depends(parse_meal())]
)
async def handle_show_greetings(meal: Meals = Arg()):
    msg = eating_manager.show_greetings(meal)
    await remove_greeting.send(msg)


@remove_greeting.got(
    "index",
    prompt="请输入删除的问候语序号，输入0以取消操作",
    parameterless=[Depends(parse_index())]
)
async def handle_remove_greeting(state: T_State, index: int = Arg()):
    meal = state["meal"]
    msg = eating_manager.remove_greeting(meal, index)
    await remove_greeting.finish(msg)


# ------------------------- Schedulers -------------------------
# 重置吃什么次数，包括夜宵
@scheduler.scheduled_job("cron", hour="6,11,17,22", minute=0, misfire_grace_time=60)
async def _():
    eating_manager.reset_count()
    logger.info("今天吃什么次数已刷新")


# 早餐提醒
@scheduler.scheduled_job("cron", hour=7, minute=0, misfire_grace_time=60)
async def time_for_breakfast():
    await eating_manager.do_greeting(Meals.BREAKFAST)
    logger.info(f"已群发早餐提醒")


# 午餐提醒
@scheduler.scheduled_job("cron", hour=12, minute=0, misfire_grace_time=60)
async def time_for_lunch():
    await eating_manager.do_greeting(Meals.LUNCH)
    logger.info(f"已群发午餐提醒")


# 下午茶/摸鱼提醒
@scheduler.scheduled_job("cron", hour=15, minute=0, misfire_grace_time=60)
async def time_for_snack():
    await eating_manager.do_greeting(Meals.SNACK)
    logger.info(f"已群发摸鱼提醒")


# 晚餐提醒
@scheduler.scheduled_job("cron", hour=18, minute=0, misfire_grace_time=60)
async def time_for_dinner():
    await eating_manager.do_greeting(Meals.DINNER)
    logger.info(f"已群发晚餐提醒")


# 夜宵提醒
@scheduler.scheduled_job("cron", hour=22, minute=0, misfire_grace_time=60)
async def time_for_midnight():
    await eating_manager.do_greeting(Meals.MIDNIGHT)
    logger.info(f"已群发夜宵提醒")
