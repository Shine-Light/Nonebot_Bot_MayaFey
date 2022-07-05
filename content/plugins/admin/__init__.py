"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/26 18:34
"""
import nonebot
from nonebot import on_command, logger, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER

from utils.admin_tools import banSb, At, MsgText
from .config import plugin_config

su = nonebot.get_driver().config.superusers
config = get_driver().config
cb_notice = plugin_config.callback_notice


ban = on_command('禁', priority=4, block=True)
@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    /禁 @user 禁言
    """
    try:
        msg = MsgText(event.json()).replace(" ", "").replace("禁", "")
        time = int("".join(map(str, list(map(lambda x: int(x), filter(lambda x: x.isdigit(), msg))))))
        # 提取消息中所有数字作为禁言时间
    except ValueError:
        time = None
    sb = At(event.json())
    gid = event.group_id
    if sb:
        baning = banSb(gid, ban_list=sb, time=time)
        try:
            async for baned in baning:
                if baned:
                    await baned
        except ActionFailed:
            await ban.finish("权限不足")
        else:
            logger.info("禁言操作成功")
            if cb_notice:  # 迭代结束再通知
                if time is not None:
                    await ban.finish("禁言操作成功")
                else:
                    await ban.finish("该用户已被禁言随机时长")
    else:
        pass


unban = on_command("解", priority=4, block=True)
@unban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sb = At(event.json())
    gid = event.group_id
    if sb:
        baning = banSb(gid, ban_list=sb, time=0)
        try:
            async for baned in baning:
                if baned:
                    await baned
        except ActionFailed:
            await unban.finish("权限不足")
        else:
            logger.info("解禁操作成功")
            if cb_notice:  # 迭代结束再通知
                await unban.finish("解禁操作成功")


kick = on_command('踢', priority=3, block=True)
@kick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
        /踢 @user 踢出某人
        """
    msg = str(event.get_message())
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
            except ActionFailed:
                await kick.finish("权限不足")
            else:
                logger.info(f"踢人操作成功")
                if cb_notice:
                    await kick.finish(f"踢人操作成功")
        else:
            await kick.finish("不能含有@全体成员")


kick_ = on_command('黑', priority=3, block=True)
@kick_.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    黑 @user 踢出并拉黑某人
    """
    msg = str(event.get_message())
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
            except ActionFailed:
                await kick_.finish("权限不足")
            else:
                logger.info(f"踢人并拉黑操作成功")
                if cb_notice:
                    await kick_.finish(f"踢人并拉黑操作成功")
        else:
            await kick_.finish("不能含有@全体成员")


set_g_admin = on_command("管理员+", priority=3, block=True, permission=SUPERUSER)


@set_g_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    管理员+ @user 添加群管理员
    """
    msg = str(event.get_message())
    logger.info(msg)
    logger.info(msg.split())
    sb = At(event.json())
    logger.info(sb)
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
            except ActionFailed:
                await set_g_admin.finish("权限不足")
            else:
                logger.info(f"设置管理员操作成功")
                await set_g_admin.finish("设置管理员操作成功")
        else:
            await set_g_admin.finish("指令不正确 或 不能含有@全体成员")


unset_g_admin = on_command("管理员-", priority=3, block=True, permission=SUPERUSER)
@unset_g_admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    管理员- @user 取消群管理员
    """
    msg = str(event.get_message())
    logger.info(msg)
    logger.info(msg.split())
    sb = At(event.json())
    logger.info(sb)
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
            except ActionFailed:
                await unset_g_admin.finish("权限不足")
            else:
                logger.info(f"取消管理员操作成功")
                await unset_g_admin.finish("取消管理员操作成功")
        else:
            await unset_g_admin.finish("指令不正确 或 不能含有@全体成员")
