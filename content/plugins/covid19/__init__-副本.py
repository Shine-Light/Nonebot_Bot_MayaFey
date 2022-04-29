from nonebot import on_regex, on_command, get_bot
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent
from nonebot import require, logger
from .data_load import DataLoader
from .tools import NewsData
from nonebot import get_driver
from ..utils import users
from .. import permission
import time



DL = DataLoader('data.json')
NewsBot = NewsData()
config = get_driver().config
timezone = str(config.timezone)
ft: str = "%Y-%m-%d %H:%M:%S"
localTime = time.strftime(ft, time.localtime())

'''

 指令:
 #add_focus   #city_news

'''
add_focus = on_command("关注疫情", priority=7)
@add_focus.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "add_focus", gid):
        citys = str(event.get_message()).strip()
        city = citys.split(" ", 1)[1]
        if NewsBot.data.get(city) and city not in FOCUS[gid]:
            FOCUS[gid].append(city)
            DL.save()
            await add_focus.finish(message=f"已添加{city}疫情推送")
        else:
            await add_focus.finish(message=f"添加失败")
    else:
        await add_focus.send("无权限")


delete_focus = on_command("取消关注疫情", priority=7)
@delete_focus.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "delete_focus", gid):
        citys = str(event.get_message()).strip()
        city = citys.split(" ", 1)[1]
        gid = str(event.group_id)
        if NewsBot.data.get(city) and city in FOCUS[gid]:
            FOCUS[gid].remove(city)
            DL.save()
            await delete_focus.finish(message=f"已取消{city}疫情推送")
        else:
            await delete_focus.finish(message=f"取消失败")
    else:
        await delete_focus.send("无权限")


city_news = on_regex(r'^(.{0,6})(疫情.{0,4})', block=True, priority=7)
@city_news.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "city_news", gid):
        msg: str = str(event.get_message()).strip()
        temp: str = msg.split("疫")[0]
        if "关注" in temp :
            await city_news.finish()
        city_name = msg.split("疫")[0]
        kw: str = "疫" + msg.split("疫")[1]

        if city:= NewsBot.data.get(city_name):
            if kw == '疫情政策':
                await city_news.finish(message=city.policy)
            elif kw == '疫情':
                await city_news.finish(message=f"数据更新时间:{NewsBot.time}\n{city.main_info}")
        else:
            await city_news.finish(message="查询的城市不存在或存在别名")
    else:
        await city_news.send("无权限")


added_list = on_command("疫情关注列表", priority=7)
@added_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    addedList: list = FOCUS[gid]
    msg = "已关注的城市:\n"
    if not addedList:
        msg = "未添加城市"
    else:
        for a in addedList:
            msg += a + "\n"
        msg = msg[:-1]
    await added_list.send(msg)


'''

 定时更新 & 定时推送

'''

FOCUS = DL.data
PUSH = {}
for gid in FOCUS.keys():
    for c in FOCUS[gid]:
        PUSH[(gid,c)] = True


scheduler = require('nonebot_plugin_apscheduler').scheduler
# @scheduler.scheduled_job('cron', hour='18', minute='00', second='00', misfire_grace_time=60) # = UTC+8 1445
@scheduler.scheduled_job("cron", hour="18", minute="30", timezone=timezone)
async def update():

    if NewsBot.update_data():
        logger.info(f"[疫情数据更新]{NewsBot.time}")

        for gid in FOCUS.keys():
            for c in FOCUS.get(gid):
                city = NewsBot.data.get(c)

                # 判定是否为更新后信息
                if city.today['isUpdated']:
                    # 判定是否未推送
                    
                    if PUSH.get((gid, c), True):
                        PUSH[(gid, c)] = False
                        await get_bot().send_group_msg(group_id=int(gid), message=f'数据更新时间,{NewsBot.time}\n' + city.main_info)
                
                else:
                    PUSH[(gid, c)] = True


