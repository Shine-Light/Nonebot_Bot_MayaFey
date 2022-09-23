"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/6/27 12:42
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message
from nonebot.params import CommandArg
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from content.plugins.permission.tools import special_per, get_special_per
from utils import users, admin_tools
from .tools import *
from content.plugins.permission.tools import permission_
from utils.other import add_target, translate, get_bot_name


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "demerit"),
    description="对群员违规行为进行记录",
    usage="/我的记过记录\n"
          "/记过 @xx @xx ... {原因} (超级用户)\n"
          "/查找记过记录 @xx (超级用户)\n"
          "/记过配置\n"
          "/修改记过配置 {配置项} {值} (超级用户)" + add_target(60)
)


demerit = on_command(cmd="记过", priority=8, block=True)
@demerit.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "demerit", str(event.group_id)):
        if len(args) < 2:
            await demerit.finish("参数有误哦~")

        if "CQ:at" not in str(args[0]):
            await demerit.finish("至少要艾特一个人哦~")

        msg = "以下成员已记过:\n"
        msg_limit = ""
        try:
            note = args[1].data["text"].strip()
        except:
            note = ""
        uids = admin_tools.At(event.json())
        gid = str(event.group_id)
        limit = get_limit(gid)

        for uid in uids:
            if str(uid) == str(bot.self_id):
                await demerit.send(f"{get_bot_name()}是做错什么了吗?!")
                continue
            uid = str(uid)
            nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid)))["nickname"]
            if permission_(users.get_role(gid, uid), "superuser"):
                await demerit.send(f"{nickname} 权限为超级用户及以上,无法记过!")
                continue
            add_demerit(gid, uid, note)

            msg += f"{nickname} 记过一次\n"

            if get_count(gid, uid) >= limit:
                msg_limit += f"{nickname}\n"

        if note.strip():
            msg += "原因:" + note
        else:
            msg += "原因:无原因"

        if len(msg.split("\n")) <= 2:
            msg = "没有人被记过"

        await demerit.send(msg)

        if msg_limit:
            msg_limit += f"记过已经超过 {limit} 次啦!"
            await demerit.send(msg_limit)
    else:
        await demerit.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'demerit')} 及以上")


get_demerit = on_command(cmd="我的记过记录", priority=8, block=True)
@get_demerit.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    count = get_count(gid, uid)
    comments = get_comments(gid, uid)
    if count == 0:
        await get_demerit.finish("表现良好,没有记过记录!")
    msg = f"总共记过 {count} 次\n"
    a = 1
    for comment in comments:
        msg += f"{a}: {comment}\n"

    await get_demerit.send(msg.strip("\n"))


admin_get_demerit = on_command(cmd="查找记过记录", priority=8, block=True)
@admin_get_demerit.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "admin_get_demerit", str(event.group_id)):
        uids = admin_tools.At(event.json())
        if len(uids) > 1:
            await admin_get_demerit.finish("一次只能查一个人的记录!")
        if len(uids) <= 0:
            await admin_get_demerit.finish("你还没说要查谁的记录呢!")
        uid = str(uids[0])
        gid = str(event.group_id)
        count = get_count(gid, uid)
        comments = get_comments(gid, uid)
        if count == 0:
            await admin_get_demerit.finish("表现良好,没有记过记录!")
        msg = f"总共记过 {count} 次\n"
        a = 1
        for comment in comments:
            msg += f"{a}: {comment}\n"
            a += 1

        await admin_get_demerit.send(msg.strip("\n"))
    else:
        await admin_get_demerit.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'admin_get_demerit')} 及以上")


demerit_config = on_command(cmd="记过配置", priority=8)
@demerit_config.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await demerit_config.send(get_config(str(event.group_id)))


set_demerit_config = on_command(cmd="修改记过配置", priority=8)
@set_demerit_config.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if special_per(users.get_role(str(event.group_id), str(event.user_id)), "set_demerit_config", str(event.group_id)):
        args = str(event.get_message()).split(" ")
        args.pop(0)
        if len(args) != 2:
            await set_demerit_config.finish("参数有误哦~")
        cfg = str(args[0])
        value = str(args[1])
        gid = str(event.group_id)
        re = set_config(gid, cfg, value)
        await set_demerit_config.send(re)
    else:
        await set_demerit_config.finish(f"无权限,权限需在 {get_special_per(str(event.group_id), 'set_demerit_config')} 及以上")
