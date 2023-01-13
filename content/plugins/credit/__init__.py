"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/25 22:30
"""
from nonebot import on_command, get_bot
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.exception import RejectedException
from nonebot.params import CommandArg
from . import tools, LuckyMoney
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from utils.other import add_target, translate
from utils.admin_tools import At

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "credit"),
    description="积分查询和排行",
    usage="/积分排行\n"
          "/我的积分\n"
          "/发红包 {积分数} {份数}\n"
          "/抢红包\n"
          "/转账 {积分数} {@xxx}" + add_target(60)
)
manager = LuckyMoney.LuckyMoneyManager()


async def timeout(gid: str):
    """
    处理过期红包
    gid: 群号
    """
    bot: Bot = get_bot()
    sender_name = (await bot.get_group_member_info(group_id=int(gid), user_id=int(manager.data.get(gid).get("uid")))).get('nickname')
    money_surplus = manager.get_money_surplus(gid)
    await bot.send_group_msg(group_id=int(gid), message=f"{sender_name} 发出的红包过期了,退还 {money_surplus} 点积分")
    manager.backMoney(gid)
    manager.removeMoney(gid)
    scheduler.remove_job(job_id=f"lucky_money_{gid}")


# 积分排行榜
top = on_command(cmd="积分排行", aliases={"积分排名", "积分排行榜", "积分前十", "积分前10"}, priority=8, block=False)
@top.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message = await tools.top(str(event.group_id), bot)
    await top.send(message=message[:-1] + add_target(60))


# 查看自己的积分
num = on_command(cmd="积分", aliases={"我的积分", "积分数", "credit"}, priority=8, block=False)
@num.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    credit = tools.get(str(event.group_id), str(event.user_id))
    await num.send(message=f"你的积分为:{credit}", at_sender=True)


send_lucky_money = on_command(cmd="发红包", aliases={"塞红包"}, priority=8, block=False)
@send_lucky_money.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if manager.exist(str(event.group_id)):
        await send_lucky_money.finish("已经有红包了,抢完再发吧")
    if not args:
        return
    args = args.extract_plain_text().strip().split(" ")
    if len(args) >= 1:
        matcher.set_arg("money", Message(args[0]))
        if len(args) >= 2:
            matcher.set_arg("count", Message(args[1]))


@send_lucky_money.got("money", prompt="要塞多少积分呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    money = matcher.get_arg("money").extract_plain_text().strip()
    if money in ["不发了", "算了", "取消"]:
        await send_lucky_money.finish("已取消")
    try:
        money = int(money)
    except:
        await send_lucky_money.send("积分要整数哦")
        await send_lucky_money.reject("要塞多少积分呢?")
    if money <= 0:
        await send_lucky_money.send("最少1积分!")
        await send_lucky_money.reject("要塞多少积分呢?")
    uid = str(event.user_id)
    gid = str(event.group_id)
    if not tools.check(gid, uid, money):
        await send_lucky_money.send("你的积分不够耶")
        await send_lucky_money.reject("要塞多少积分呢?")


@send_lucky_money.got("count", prompt="要分成几份呢?")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    uid = str(event.user_id)
    gid = str(event.group_id)
    money = int(matcher.get_arg("money").extract_plain_text().strip())
    count = matcher.get_arg("count").extract_plain_text().strip()
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))['nickname']
    if count in ["不发了", "算了", "取消"]:
        await send_lucky_money.finish("已取消")
    try:
        count = int(count)
        if count <= 0:
            raise RejectedException()
    except RejectedException:
        await send_lucky_money.send("最少一份啦!")
        await matcher.reject(prompt="要分成几份呢?")
    except:
        await send_lucky_money.send("份数要整数哦")
        await matcher.reject(prompt="要分成几份呢?")
    if count > money:
        await send_lucky_money.send(f"不是吧不是吧,连 {money} 点积分都要拆成 {count} 份来发吗?")
        await matcher.reject(prompt="要分成几份呢?")
    manager.sendMoney(gid, uid, nickname, money, count)
    scheduler.add_job(func=timeout, trigger="interval", args=[gid], id=f"lucky_money_{gid}", minutes=5)
    tools.minus(gid, uid, money)
    await send_lucky_money.send("发送成功,快来抢红包呀!")
    await send_lucky_money.send(MessageSegment.image(await manager.generateSendImg(gid)))


get_lucky_money = on_command(cmd="抢红包", priority=8, block=False)
@get_lucky_money.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))['nickname']
    if not manager.exist(gid):
        await get_lucky_money.finish("现在没有红包可以抢哦,快去发一个吧!")
    if manager.is_got(gid, uid):
        await get_lucky_money.finish("太贪心了啊喂,每人只能抢一份!")
    money = manager.getMoney(gid, uid, nickname)
    await get_lucky_money.send(f"太棒了!你抢到了 {money} 积分", at_sender=True)
    if not manager.get_count_surplus(gid):
        fortunate = manager.fortunate(gid)
        fortunate_id = fortunate[0]
        fortunate_count = manager.get_record(gid).index(fortunate) + 1
        fortunate_money = fortunate[1]
        fortunate_name = (await bot.get_group_member_info(group_id=int(gid), user_id=int(fortunate_id), no_cache=True))['nickname']
        await get_lucky_money.send(
            Message([
                MessageSegment.text(f"红包抢完了!\n本次的手气王是: {fortunate_name}({fortunate_id}), TA在第 {fortunate_count} 次抢到了 {fortunate_money} 积分"),
                MessageSegment.image(await manager.generateEndImg(gid))
            ]))
        manager.removeMoney(gid)
        scheduler.remove_job(job_id=f"lucky_money_{gid}")


transfer_credit = on_command(cmd="转账", aliases={"打钱"}, priority=8, block=False)
@transfer_credit.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if len(event.original_message) >= 1 and len(args) >= 1:
        matcher.set_arg("credit", Message(args[0]))
        if len(event.original_message) >= 2:
            matcher.set_arg("at", Message(event.original_message[1:-1]))


@transfer_credit.got(key="credit", prompt="转多少呢")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    try:
        credit = int(matcher.get_arg("credit").extract_plain_text())
        gid = str(event.group_id)
        uid = str(event.user_id)
        if not tools.check(gid, uid, credit):
            await transfer_credit.finish("你的积分不够哦")
        if credit <= 0:
            await transfer_credit.finish("最少1积分!")
            await transfer_credit.reject("转多少呢")
    except ValueError:
        await transfer_credit.send("积分要整数哦")
        await transfer_credit.reject("转多少呢")


@transfer_credit.got(key="at", prompt="转个谁呢(艾特TA)")
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    credit = int(matcher.get_arg("credit").extract_plain_text())
    uid = str(event.user_id)
    gid = str(event.group_id)
    at = At(event.original_message)
    if not at:
        await transfer_credit.finish("转账给空气吗?")
    if len(at) != 1:
        await transfer_credit.send("只能转给一人!")
        await transfer_credit.reject("转个谁呢(艾特TA)")
    if at[0] == uid:
        await transfer_credit.send("不能转给自己!")
        await transfer_credit.reject("转个谁呢(艾特TA)")

    tools.minus(gid, uid, credit)
    tools.add(gid, at[0], credit)

    await transfer_credit.send("转账成功!")
