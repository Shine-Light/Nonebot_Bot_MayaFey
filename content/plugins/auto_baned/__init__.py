"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/9/16 21:35
"""
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent, GroupRequestEvent, GroupIncreaseNoticeEvent, Bot
from nonebot.plugin import on_notice, on_request, require, PluginMetadata
from nonebot.log import logger
from .tools import *
from utils.other import translate, add_target

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "auto_baned"),
    description=f"在入群后 {delta_time} 分钟内退群将直接纳入黑名单",
    usage="被动,无命令" + add_target(60)
)

baned_record = on_notice(priority=4, block=False)
@baned_record.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    if event.sub_type == "leave" and (await is_time_to_baned(uid, gid)):
        auto_baned_config_path = auto_baned_path / gid / "baned.json"
        js = json_load(auto_baned_config_path)
        js.update({uid: ""})
        json_write(auto_baned_config_path, js)
        await baned_clean(bot)


member_join_time = on_notice(priority=4, block=False)
@member_join_time.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    uid = str(event.user_id)
    if uid == bot.self_id:
        return
    gid = str(event.group_id)
    auto_baned_config_path = auto_baned_path / gid / "time.json"
    js = json_load(auto_baned_config_path)
    join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    js.update({uid: join_time})
    json_write(auto_baned_config_path, js)


baned_check = on_request(rule=checker_group_request(), priority=4, block=False)
@baned_check.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    if await is_baned(uid, gid):
        await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=False, reason="你已被防白嫖系统拉黑")


clean_out_record = require("nonebot_plugin_apscheduler").scheduler
@clean_out_record.scheduled_job(trigger="cron", hour=0)
async def auto_baned_clean():
    bot: Bot = get_bot()
    try:
        await baned_clean(bot)
    except Exception as e:
        logger.error("自动清理退群拉黑过期文件信息:" + str(e))
    logger.info("自动清理退群拉黑过期信息")
