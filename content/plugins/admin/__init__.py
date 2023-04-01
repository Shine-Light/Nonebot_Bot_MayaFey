"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/26 18:34
"""
import nonebot
from nonebot import on_command, logger, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg

from utils.other import add_target
from utils.admin_tools import banSb, At, banWholeGroup
from .config import plugin_config


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="admin",
    description="禁言,解禁,踢出,拉黑等...",
    usage="/禁 @xx @xx ... {时间}\n"
          "/解 @xx @xx ...\n"
          "/踢 @xx @xx ...\n"
          "/黑 @xx @xx ...\n"
          "/全员禁\n"
          "/解全员禁\n"
          "/管理员+ @xx @xx\n"
          "/管理员- @xx @xx\n"
          "/设置头衔 @xx @xx {头衔}\n"
          "/取消头衔 @xx @xx" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "superuser",
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "群管",
    }
)


su = nonebot.get_driver().config.superusers
config = get_driver().config


ban = on_command('禁', priority=4, block=False)
@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """
    /禁 @user 禁言
    """
    try:
        time = int(args.extract_plain_text().strip())
    except ValueError:
        time = None
    sb = At(event.original_message)
    gid = event.group_id
    if sb:
        try:
            await banSb(gid, ban_list=sb, time=time)
        except ActionFailed as e:
            await ban.finish(str(e))
        logger.info("禁言操作成功")
        if time is not None:
            await ban.finish("禁言操作成功")
        else:
            await ban.finish("该用户已被禁言随机时长")


unban = on_command("解", priority=4, block=False)
@unban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sb = At(event.json())
    gid = event.group_id
    if sb:
        try:
            await banSb(gid, ban_list=sb, time=0)
        except ActionFailed as e:
            await unban.finish(str(e))
        logger.info("解禁操作成功")
        await unban.finish("解禁操作成功")


kick = on_command('踢', priority=3, block=False)
@kick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    /踢 @user 踢出某人
    """
    sb = At(event.json())
    gid = event.group_id
    if sb:
        if 'all' not in sb:
            try:
                for qq in sb:
                    await bot.set_group_kick(
                        group_id=gid,
                        user_id=int(qq),
                        reject_add_request=False
                    )
            except ActionFailed as e:
                await kick.finish(str(e))
            logger.info(f"踢人操作成功")
            await kick.finish(f"踢人操作成功")
        else:
            await kick.finish("不能含有@全体成员")


kick_ = on_command('黑', priority=3, block=False)
@kick_.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    黑 @user 踢出并拉黑某人
    """
    sb = At(event.json())
    gid = event.group_id
    if sb:
        if 'all' not in sb:
            try:
                for qq in sb:
                    await bot.set_group_kick(
                        group_id=gid,
                        user_id=int(qq),
                        reject_add_request=True
                    )
            except ActionFailed as e:
                await kick_.finish(str(e))
            logger.info(f"踢人并拉黑操作成功")
            await kick_.finish(f"踢人并拉黑操作成功")
        else:
            await kick_.finish("不能含有@全体成员")


set_g_admin = on_command("管理员+", priority=3, block=False, permission=SUPERUSER)
@set_g_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    管理员+ @user 添加群管理员
    """
    sb = At(event.json())
    gid = event.group_id
    if sb:
        if 'all' not in sb:
            try:
                for qq in sb:
                    await bot.set_group_admin(
                        group_id=gid,
                        user_id=int(qq),
                        enable=True
                    )
            except ActionFailed as e:
                await unban.finish(str(e))
            logger.info(f"设置管理员操作成功")
            await set_g_admin.send("设置管理员操作成功")
        else:
            await set_g_admin.finish("指令不正确 或 不能含有@全体成员")


unset_g_admin = on_command("管理员-", priority=3, block=False, permission=SUPERUSER)
@unset_g_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    管理员- @user 取消群管理员
    """
    sb = At(event.json())
    gid = event.group_id
    if sb:
        if 'all' not in sb:
            try:
                for qq in sb:
                    await bot.set_group_admin(
                        group_id=gid,
                        user_id=int(qq),
                        enable=False
                    )
            except ActionFailed as e:
                await unban.finish(str(e))
            else:
                logger.info(f"取消管理员操作成功")
                await unset_g_admin.send("取消管理员操作成功")
        else:
            await unset_g_admin.finish("指令不正确 或 不能含有@全体成员")


ban_all = on_command(cmd="全员禁", aliases={"禁言全员", "禁言全员", "禁言所有人", "禁全员"}, priority=3, block=False)
@ban_all.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    try:
        await banWholeGroup(gid=gid, enable=True)
    except ActionFailed as e:
        await unban.finish(str(e))
    logger.info(f"禁言全员操作成功")
    await ban_all.finish(f"禁言全员操作成功")


un_ban_all = on_command(cmd="解全员禁", aliases={"解禁全员", "全员解禁", "解禁所有人"}, priority=3, block=False)
@un_ban_all.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    try:
        await banWholeGroup(gid=gid, enable=False)
    except ActionFailed as e:
        await unban.finish(str(e))
    logger.info(f"解禁全员操作成功")
    await un_ban_all.finish(f"解禁全员操作成功")


title_set = on_command(cmd="设置头衔", aliases={"设置称号"}, priority=5, block=False)
@title_set.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    title = args.extract_plain_text().strip()
    sb = At(event.original_message)
    if sb:
        if not title:
            await title_set.finish("头衔呢?")
        if "all" in sb:
            await title_set.finish("不能为全部人设置头衔!")

        try:
            for uid in sb:
                await bot.set_group_special_title(group_id=event.group_id, user_id=int(uid), special_title=title, duration=-1)
        except ActionFailed as e:
            await title_set.finish(f"设置失败,{str(e)}")
        await title_set.send("设置成功!")


title_unset = on_command(cmd="取消头衔", aliases={"取消称号"}, priority=5, block=False)
@title_unset.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sb = At(event.original_message)
    if sb:
        if "all" in sb:
            await title_unset.finish("不能取消所有人的头衔!")
        try:
            for uid in sb:
                await bot.set_group_special_title(group_id=event.group_id, user_id=int(uid))
        except ActionFailed as e:
            await title_unset.finish(f"取消失败,{str(e)}")
        await title_unset.send("取消成功!")



