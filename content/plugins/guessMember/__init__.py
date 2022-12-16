"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/12/8 22:05
"""
from nonebot import on_command, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

from utils import users
from utils.permission import special_per, get_special_per
from utils.other import translate, add_target
from .data_source import guessMember
from .config import Config
from utils.other import get_bot_name

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "guessMember"),
    description="猜群友",
    usage="/猜群友\n"
          "/猜 @某人\n"
          "/结束猜群友\n"
          "/猜群友配置\n"
          "/猜群友设置 {配置项} {配置值} (超级用户)" + add_target(60)
)

settings = {
    Config.set_cost: {"消耗积分", "消耗"},
    Config.set_bonus: {"奖励积分", "奖励"},
    Config.set_out_time: {"过期时间", "超时时间"},
    Config.set_bot_enable: get_driver().config.nickname.union({"机器人", "bot", "抽到机器人"}),
    Config.set_active_time: {"潜水时间阈值", "活跃时间阈值"},
    Config.set_only_active: {"活跃", "潜水成员不参与"},
    Config.set_self_enable: {"自己", "抽到自己"},
    Config.set_cut_length: {"头像切割大小百分比", "头像百分比", "切割百分比"}
}

guessMember = guessMember()


newGuess = on_command(cmd="猜群友", aliases={"猜群员", "guessMember"}, priority=8, block=False)
@newGuess.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    credit_check = guessMember.credit_check(gid, uid)
    if credit_check:
        await newGuess.finish(credit_check)
    if guessMember.gameExist(gid):
        await newGuess.finish(f"人太多{get_bot_name()}会忙不过来的!")
    target_data = guessMember.choice_target(uid, gid, await bot.call_api(api="get_group_member_list", group_id=event.group_id, no_cache=True))
    if not target_data:
        await newGuess.finish(Message("没有符合条件的群友了[CQ:face,id=174]"))
    guessMember.gameStart(gid, uid, bot, target_data)
    await newGuess.send(Message([MessageSegment.text(f"游戏开始!花费 {guessMember.get_cost(gid)} 点积分,将发送第一条线索")] + guessMember.get_clue(gid)))


guess = on_command(cmd="猜", aliases={"我猜", "我猜是"}, priority=8, block=False)
@guess.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    if not guessMember.gameExist(gid):
        await guess.finish("游戏还没开呢")
    if not guessMember.is_active(gid):
        await guess.finish(f"{get_bot_name()}已经忘了上一局了,再开一局把!")
    if not guessMember.operator_check(gid, uid):
        await guess.finish("其他人不要来捣乱啦")
    msg: Message = event.original_message
    if len(msg) == 1:
        await guess.finish("猜猜你是谁?猜不到呀!")
    elif len(msg) > 2:
        while True:
            if len(msg) > 2 and msg[2].data['text'].strip() == "":
                msg.pop(2)
                continue
            elif len(msg) > 2:
                await guess.finish("你是打算把所有人都试一遍吗?")
                break
            else:
                break
    if msg[1].type != "at":
        await guess.finish("猜猜你是谁?猜不到呀!")
    msg: MessageSegment = msg[1]
    target_id = str(msg.data['qq'])
    if guessMember.is_target(gid, target_id):
        await guess.finish(guessMember.Win(gid))
    else:
        await guess.send(guessMember.guessError(gid))


guessStop = on_command(cmd="不猜了", aliases={"终止猜群友", "结束猜群友", "终止猜群员", "结束猜群员"})
@guessStop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    if guessMember.gameExist(gid):
        await guessStop.finish("没有开始怎么结束?")
    elif not guessMember.operator_check(gid, uid):
        await guess.finish("其他人不要来捣乱啦")
    else:
        await guessStop.finish(guessMember.gameStop(gid))


guessConfig = on_command(cmd="猜群友配置", aliases={"猜群员配置"}, priority=8, block=False)
@guessConfig.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gameConfig = Config(str(event.group_id))
    await guessConfig.finish(str(gameConfig))


guessSetting = on_command("猜群友设置", aliases={"猜群员设置"}, block=False, priority=8)
@guessSetting.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "guessSetting", gid):
        args = args.extract_plain_text().split(" ")
        try:
            args.remove("")
        except:
            pass
        if len(args) == 1:
            matcher.set_arg("option", Message(args[0]))
        elif len(args) == 2:
            matcher.set_arg("option", Message(args[0]))
            matcher.set_arg("choice", Message(args[1]))
    else:
        await guessSetting.finish(
            f"无权限,权限需在 {get_special_per(gid, 'guessSetting')} 及以上")


@guessSetting.got("option", prompt="要设置什么呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    args = matcher.get_arg("option").extract_plain_text()
    option = None
    for setting in settings:
        if args in settings[setting]:
            option = setting
            state['option'] = option
            break

    if not option:
        await guessSetting.finish(Message(f"没有 {args} 配置项哦"))


@guessSetting.got("choice", prompt="要设置成什么呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    choice = matcher.get_arg("choice").extract_plain_text()
    option = state['option']
    gameConfig = Config(str(event.group_id))
    re = option(gameConfig, choice)
    if re:
        await guessSetting.finish(re)
    await guessSetting.finish("设置成功!")
