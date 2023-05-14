"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/4/21 12:51
"""
from nonebot import on_command, require, get_bot, get_driver
from nonebot.exception import FinishedException, ActionFailed
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, PrivateMessageEvent
from . import tools
from utils.other import add_target, reboot
from nonebot.plugin import PluginMetadata


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="update",
    description="机器人更新",
    usage="/检查更新 (超级用户)\n"
          "/更新 (超级用户)\n"
          "/更新日志 (超级用户)" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "superuser",
        "unset": True,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "更新",
    }
)


update = on_command("更新", aliases={"update"}, priority=2, block=True)
@update.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        if await tools.check_update():
            state = await tools.get_state(await tools.get_version_last())
            if state["auto"]:
                await update.send("更新前记得备份哦,是否确认更新?(Y\\N)")
            else:
                await update.finish(f"本次更新无法自动更新,请手动升级\n备注:{state['note']}")
        else:
            await update.finish("已经是最新版本,无需更新")
    except FinishedException:
        raise FinishedException()
    except Exception as e:
        await update.finish(f"更新出错: {str(e)}")


@update.got("choice")
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    choice = matcher.get_arg("choice")
    if event.dict().get("group_id"):
        target = str(event.group_id)
        type = "group"
    else:
        target = str(event.user_id)
        type = "private"
    try:
        if choice.extract_plain_text().upper() in ["Y", "是", "确认", "更新", "确认更新"]:
            await update.send("正在自动更新,更新期间机器人无法使用,请勿关闭程序")
            await tools.update(target, type)
            await update.send("正在重启...")
            reboot()
        else:
            await update.send("取消更新...")
    except Exception as e:
        await update.finish(f"更新出错: {str(e)}")


check_update = on_command("检查更新", aliases={"check_update"}, priority=8, block=False)
@check_update.handle()
async def _(bot: Bot, event: MessageEvent):
    if await tools.check_update():
        state = await tools.get_state(await tools.get_version_last())
        if state["auto"]:
            await check_update.finish("检测到有新版本,请及时更新,更新前记得备份")
        else:
            await update.send(f"本次更新无法自动更新,请手动升级\n备注:{state['note']}")
    else:
        await check_update.finish("已经是最新版本")


update_log = on_command("更新日志", aliases={"update_log", "更新记录"}, priority=8, block=False)
@update_log.handle()
async def _(bot: Bot, event: MessageEvent):
    img = await tools.get_update_log()
    await update_log.send(MessageSegment.image(img) + MessageSegment.text("完整日志地址:https://mayafey.shinelight.xyz/updatelog/"))


update_ignore = on_command("忽略更新", aliases={"忽略本次更新", "跳过更新", "跳过本次更新"}, priority=8, block=False)
@update_ignore.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    if await tools.get_version_last() != tools.get_version():
        version_current = await tools.get_version_last()
        tools.ignore_update(version_current)
        await update_ignore.send("已忽略本次更新,将会在下次重启或更新时再次提醒")
    else:
        await update_ignore.send("已是最新版本,无需忽略更新")


timezone = "Asia/Shanghai"
scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job("interval", minutes=30, timezone=timezone)
async def run():
    if await tools.check_update():
        logger.info("检测到新版本,向根用户推送更新信息")
        bot: Bot = get_bot()
        for superuser in get_driver().config.superusers:
            try:
                await bot.send_private_msg(user_id=int(superuser), message="检测到有新版本,请及时更新,更新前记得备份")
            except ActionFailed:
                logger.error(f"向根用户 {superuser} 发起会话失败")
            except Exception as e:
                logger.error(f"发送好友请求提示失败,{str(e)}")
