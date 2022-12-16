"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/1 22:24
"""
import random
import ujson as json

from nonebot import on_command, on_notice, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment, Event, GroupDecreaseNoticeEvent
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, T_State
from utils.other import translate, add_target
from utils import users
from utils.permission import get_special_per, special_per
from .data import DailyWife, Config, Record

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "DailyWife"),
    description="随机抽取群友做老婆",
    usage="/抽老婆\n"
          "/我的老婆\n"
          "/抽老婆配置\n"
          "/抽老婆设置 {设置项} {设置值} (超级用户,可交互)\n\n"
          "设置项|设置值|功能:\n"
          "\t渣男 开|关 可以换老婆\n"
          "\tNTR 开|关 可以抽到同一个人\n"
          "\t无视性别 开|关 可以南/钕通\n" 
          "\t机器人 开|关 可以抽到机器人\n" 
          "\t自己 开|关 可以抽到自己\n" 
          "\t潜水成员不参与 开|关 不会抽到潜水的人\n" 
          "\t潜水时间阈值 整数 超过时间阈值视为潜水\n" + add_target(60)
)

nicknames = get_driver().config.nickname
called = ["老婆", "媳妇", "亲爱的", "娘子", "宝贝", "小可爱"]
call_: set = set({})
for call in called:
    call_.add("我的" + call)
message_daily = "今天你的 {called} 是\n" \
                "{pic}\n" \
                "{wife_name}({wife_uid})"

message_change = "你的新 {called} 是\n" \
                 "{pic}\n" \
                 "{wife_name}({wife_uid})\n" \
                 "{old_wife_name} 被 {user_name} 抛弃了"

message_change_failed = ["渣男,你在想什么啊!"]

message_change_again = "你的新 {called} 是\n" \
                       "{pic}\n" \
                       "{wife_name}({wife_uid})\n" \
                       "{user_name}没有逃脱命运的安排"

message_random_failed = ["选妻条件太苛刻了,没有符合条件的群友[CQ:face,id=176]"]

message_have_not_wife = ["你还是单身狗一条呢,快去抽个老婆吧"]

message_wife_run = ["{wife_name} 丢下 {user_name} 跑了"]
message_user_run = ["{user_name} 丢下 {wife_name} 跑了"]

message_config = "当前群的随机老婆配置:\n" \
                 "渣男: {scum}\n" \
                 "NTR: {NTR}\n" \
                 "无视性别: {same_gender}\n" \
                 "抽到机器人: {bot}\n" \
                 "抽到自己: {Self}\n" \
                 "潜水成员不参与: {activity}\n" \
                 "潜水时间阈值: {activity_time} 天"

settings = {
    Config.set_scum: {"渣男", "scum"},
    Config.set_NTR: {"NTR", "牛头人"},
    Config.set_same_gender: {"同性", "无视性别", "same_gander"},
    Config.set_bot: nicknames.union({"机器人", "bot"}),
    Config.set_Self: {"自己", "Self", "self", "myself"},
    Config.set_activity: {"活跃", "activity", "潜水成员不参与"},
    Config.set_activity_time: {"activity_time", "活跃时间", "活跃阈值", "潜水时间阈值"},
}

avatar_api_url = "https://q1.qlogo.cn/g?b=qq&nk={uid}&s=640"


def bool2text(choice: bool) -> str:
    if choice:
        return "开"
    else:
        return "关"


myWife = on_command("我的老婆", aliases=call_, block=False, priority=8)
@myWife.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    operator = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id, no_cache=True)
    operator['user_id'] = str(operator['user_id'])
    member_list = await bot.call_api(api="get_group_member_list", group_id=event.group_id, no_cache=True)
    dailywife = DailyWife(operator, member_list)
    await dailywife.init()
    if dailywife.have_wife():
        wife = await bot.get_group_member_info(group_id=event.group_id, user_id=(int(await dailywife.record.get_wife_id(operator))))
        avatar_url = avatar_api_url.replace("{uid}", str(wife['user_id']))
        message_text = message_daily \
            .replace("{called}", random.choice(called)) \
            .replace("{wife_name}", wife['nickname']) \
            .replace("{wife_uid}", str(wife['user_id'])) \
            .replace("{user_name}", operator['nickname'])
        message = []
        for msg in message_text.splitlines():
            if msg == "{pic}":
                message.append(MessageSegment.image(avatar_url))
            else:
                message.append(MessageSegment.text(msg + "\n"))

        await dailyWife.send(Message(message), at_sender=True)
    else:
        await myWife.send(Message(random.choice(message_have_not_wife)))


dailyWife = on_command("抽老婆", aliases={"随机老婆"}, block=False, priority=8)
@dailyWife.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    operator = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id, no_cache=True)
    operator['user_id'] = str(operator['user_id'])
    member_list = await bot.get_group_member_list(group_id=event.group_id)
    dailywife = DailyWife(operator, member_list)
    await dailywife.init()
    if operator['user_id'] in (await dailywife.record.get_selected_list()):
        if dailywife.config.scum:
            old_wife_id = await dailywife.record.get_wife_id(operator)
            old_wife = await bot.get_group_member_info(user_id=old_wife_id, group_id=event.group_id, no_cache=True)
            wife = await dailywife.randomWife()
            if not wife:
                await dailyWife.finish(Message(random.choice(message_random_failed)))
            avatar_url = avatar_api_url.replace("{uid}", wife['user_id'])
            if old_wife_id == wife['user_id']:
                message_ = message_change_again
            else:
                message_ = message_change
            message_text = message_ \
                .replace("{called}", random.choice(called)) \
                .replace("{wife_name}", wife['nickname']) \
                .replace("{wife_uid}", str(wife['user_id'])) \
                .replace("{old_wife_name}", old_wife['nickname']) \
                .replace("{user_name}", operator['nickname'])

            message = []
            for msg in message_text.splitlines():
                if msg == "{pic}":
                    message.append(MessageSegment.image(avatar_url))
                else:
                    message.append(MessageSegment.text(msg + "\n"))

            await dailyWife.send(Message(message), at_sender=True)

        else:
            await dailyWife.send(random.choice(message_change_failed), at_sender=True)

    else:
        wife = await dailywife.randomWife()
        if not wife:
            await dailyWife.finish(Message(random.choice(message_random_failed)))
        avatar_url = avatar_api_url.replace("{uid}", str(wife['user_id']))
        message_text = message_daily \
            .replace("{called}", random.choice(called)) \
            .replace("{wife_name}", wife['nickname']) \
            .replace("{wife_uid}", str(wife['user_id'])) \
            .replace("{user_name}", operator['nickname'])

        message = []
        for msg in message_text.splitlines():
            if msg == "{pic}":
                message.append(MessageSegment.image(avatar_url))
            else:
                message.append(MessageSegment.text(msg + "\n"))

        await dailyWife.send(Message(message), at_sender=True)


dailyWife_config = on_command("抽老婆配置", aliases={"随机老婆配置"}, block=False, priority=8)
@dailyWife_config.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    config = Config(str(event.group_id))
    await config.init()
    message = message_config \
        .replace("{scum}", bool2text(config.scum)) \
        .replace("{NTR}", bool2text(config.NTR)) \
        .replace("{same_gender}", bool2text(config.same_gender)) \
        .replace("{bot}", bool2text(config.bot)) \
        .replace("{Self}", bool2text(config.Self)) \
        .replace("{activity}", bool2text(config.activity)) \
        .replace("{activity_time}", str(config.activity_time))
    await dailyWife_config.send(Message(message))


dailyWife_setting = on_command("抽老婆设置", aliases={"随机老婆设置"}, block=False, priority=8)
@dailyWife_setting.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, matcher: Matcher, args: Message = CommandArg()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "dailyWife_setting", gid):
        config = Config(str(event.group_id))
        await config.init()
        args = args.extract_plain_text().split(" ")
        try:
            args.remove("")
        except:
            pass

        if len(args) >= 1:
            matcher.set_arg("option", Message(MessageSegment.text(args[0])))

            if len(args) == 2:
                matcher.set_arg("choice", Message(MessageSegment.text(args[1])))

        state['config'] = config
    else:
        await dailyWife_setting.finish(
            f"无权限,权限需在 {get_special_per(gid, 'dailyWife_setting')} 及以上")


@dailyWife_setting.got("option", prompt="要设置什么呢?")
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, matcher: Matcher):
    args = matcher.get_arg("option").extract_plain_text()
    option = None
    for setting in settings:
        if args in settings[setting]:
            option = setting
            state['option'] = option
            break

    if not option:
        await dailyWife_setting.finish(Message(f"没有 {args} 配置项哦"))


@dailyWife_setting.got("choice", prompt="要设置成什么呢?")
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, matcher: Matcher):
    choice = matcher.get_arg("choice").extract_plain_text()
    option = state['option']
    config = state['config']
    if option == Config.set_activity_time:
        try:
            activity_time = int(choice)
        except:
            await dailyWife_setting.finish("时间必须为整数!")
        if activity_time <= 0:
            await dailyWife_setting.finish("最少1天!")
        await option(config, activity_time)
    else:
        if choice in ["开", "开启", "真", "on", "True", "On", "true", "1"]:
            choice = True
        elif choice in ["关", "关闭", "假", "off", "False", "Off", "false", "0"]:
            choice = False
        else:
            await dailyWife_setting.finish(Message("? 开还是不开?"))

        await option(config, choice)

    await dailyWife_setting.send("设置成功!")


# 退群检测
def checker_leave():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'group_decrease':
            return True

    return Rule(_checker)


SomeOneRun = on_notice(rule=checker_leave(), block=False, priority=4)
@SomeOneRun.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    record = Record(str(event.group_id))
    await record.init()
    uid = str(event.user_id)
    selected_list = await record.get_selected_list()
    if uid in selected_list:
        user_name = (await bot.get_stranger_info(user_id=int(uid)))['nickname']
        wife_name = (await bot.get_stranger_info(user_id=int(selected_list[uid])))['nickname']
        message = random.choice(message_user_run) \
            .replace("{user_name}", user_name) \
            .replace("{wife_name}", wife_name)
        await SomeOneRun.send(Message(message))
        await record.deleteUser({"user_id": uid})

    for selected in selected_list:
        if uid == selected_list[selected]:
            user_name = (await bot.get_stranger_info(user_id=event.user_id))['nickname']
            wife_name = (await bot.get_stranger_info(user_id=selected_list[uid]))['nickname']
            message = random.choice(message_wife_run) \
                .replace("{user_name}", user_name) \
                .replace("{wife_name}", wife_name)
            await SomeOneRun.send(Message(message))
            await record.deleteWife({"user_id": uid})
