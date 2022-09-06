"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/9/3 17:01
"""
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, Bot, PrivateMessageEvent
from nonebot.params import CommandArg
from nonebot.matcher import Matcher

from .tools import *

friends_request_query = on_command(cmd="查询好友请求", aliases={"好友请求列表"}, permission=SUPERUSER, priority=7)
@friends_request_query.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    requestList = getRequestList()
    if not requestList:
        await friends_request_query.finish("目前无好友请求记录")
    msg = "QQ\t\t\t昵称\t\t时间\n"
    for uid in requestList:
        nickname = (await bot.get_stranger_info(user_id=int(uid), no_cache=True))['nickname']
        msg += f"{uid}   {nickname}   {requestList[uid]['time']}\n"

    await friends_request_query.finish(msg.strip("\n"))


friends_request_details = on_command(cmd="好友请求细节", permission=SUPERUSER, priority=7)
@friends_request_details.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("uid", args)


@friends_request_details.got(key="uid", prompt="请输入要查询的QQ")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    try:
        msg = getRequestDetail(matcher.get_arg("uid").extract_plain_text())
    except KeyError:
        msg = "查询不到该记录,请确认QQ是否存在"
    except Exception as e:
        msg = f"未知错误: {str(e)}"

    await friends_request_details.finish(msg)


accept_request = on_command(cmd="接受请求", aliases={"同意请求", "接受好友请求", "同意好友请求"}, permission=SUPERUSER, priority=7)
@accept_request.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    t = args.extract_plain_text().split(" ")
    try:
        t.remove("")
    except:
        pass
    if len(t) == 1:
        matcher.set_arg("uid", Message(t[0]))
    elif len(t) == 2:
        matcher.set_arg("uid", Message(t[0]))
        matcher.set_arg("remark", Message(t[1]))


@accept_request.got("uid", "请输入同意请求的QQ")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    uid = matcher.get_arg("uid").extract_plain_text()
    try:
        matcher.set_arg("flag", Message(getRequestFlag(uid)))
    except KeyError:
        await accept_request.finish("查询不到该记录,请确认QQ是否存在")
    except Exception as e:
        await accept_request.finish(f"未知错误: {str(e)}")


@accept_request.got("remark", "输入备注信息(发送 '空' 则为不备注)")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    uid = matcher.get_arg("uid").extract_plain_text()
    remark = matcher.get_arg("remark").extract_plain_text()
    flag = matcher.get_arg("flag").extract_plain_text()
    if remark == "空":
        remark = ""
    deleteRequest(uid)
    try:
        await bot.set_friend_add_request(flag=flag, approve=True, remark=remark)
    except:
        await accept_request.finish("操作失败,可能是请求已过期,前往go-cqhttp查看详情")

    await accept_request.send("操作成功")


reject_request = on_command(cmd="拒绝请求", aliases={"拒绝好友请求"}, permission=SUPERUSER, priority=7)
@reject_request.handle()
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("uid", args)


@reject_request.got("uid", "请输入拒绝请求的QQ")
async def _(bot: Bot, event: PrivateMessageEvent, matcher: Matcher):
    uid = matcher.get_arg("uid").extract_plain_text()
    try:
        flag = getRequestFlag(uid)
        await bot.set_friend_add_request(flag=flag, approve=False)
    except KeyError:
        await accept_request.finish("查询不到该记录,请确认QQ是否存在")
    except Exception as e:
        await accept_request.finish(f"未知错误: {str(e)}")

    await reject_request.send("操作成功")
