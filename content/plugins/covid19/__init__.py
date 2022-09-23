from nonebot import on_regex, on_command, get_bot, get_driver, on_endswith
from nonebot import require, logger
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.message import Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State
from nonebot.params import State, CommandArg
from nonebot.plugin import PluginMetadata

from .data import CITY_ID
from .data_load import DataLoader
from .uilts import send_msg, send_forward_msg_group
from .policy import get_city_poi_list, get_policy
from .tools import NewsBot

from utils.other import translate, add_target

DL = DataLoader('data.json')

__help__ = """---疫情信息 指令列表---
/关注疫情 + 城市 （/关注疫情 深圳）
/取消关注疫情 + 城市 （/取消关注疫情 深圳）
城市 + 疫情 （深圳疫情）
城市 + 疫情政策 （深圳疫情政策）
城市 + 风险地区  （深圳风险地区） 
"""

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "covid19"),
    description="查询各地疫情信息",
    usage=__help__ + add_target(60)
)

follow = on_command("关注疫情", priority=8, block=False)
unfollow = on_command("取消关注疫情", priority=8, block=False, aliases={"取消疫情", "取消推送疫情"})

covid19_news = on_endswith("疫情", block=False, priority=8)
covid19_policy = on_endswith(["疫情政策", "出行政策"], block=False, priority=8)
city_poi_list = on_endswith('风险地区', block=False, priority=8)

city_travel = on_regex(r"(.{2,4})到(.{2,4})", block=False, priority=8)


@follow.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State(), city: Message = CommandArg()):
    city = city.extract_plain_text()
    if "group" in event.get_event_name():
        gid = str(event.group_id)
    else:
        gid = str(event.user_id)

    if NewsBot.data.get(city) and city not in FOCUS[gid]:
        FOCUS[gid].append(city)
        DL.save()
        await follow.finish(message=f"已添加{city}疫情推送")
    else:
        await follow.finish(message=f"添加失败")


@unfollow.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State(), city: Message = CommandArg()):
    city = city.extract_plain_text()

    if event.message_type == "group":
        id = str(event.group_id)
    else:
        id = str(event.user_id)

    if NewsBot.data.get(city) and city in FOCUS[id]:
        FOCUS[id].remove(city)
        DL.save()
        await unfollow.finish(message=f"已取消{city}疫情推送")
    else:
        await unfollow.finish(message=f"取消失败")


@covid19_news.handle()
async def _(bot: Bot, event: MessageEvent):
    city_name = str(event.get_message())[:-2]
    city = NewsBot.data.get(city_name)

    if city:
        await covid19_news.send(message=f"{NewsBot.time}\n{city.main_info}")
    else:
        await covid19_news.finish(message="查询的城市不存在或存在别名")


@covid19_policy.handle()
async def _(bot: Bot, event: MessageEvent):
    city = str(event.get_message())[:-4]
    if city in CITY_ID:
        await send_msg(bot, event, get_policy(CITY_ID[city]))


@city_poi_list.handle()
async def _(bot: Bot, event: MessageEvent):
    city = str(event.get_message())[:-4]
    if city in CITY_ID:
        await send_msg(bot, event, get_city_poi_list(CITY_ID[city]))


@city_travel.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    city_A, city_B = state['_matched_groups']
    if city_A in CITY_ID and city_B in CITY_ID:
        await send_msg(bot, event, get_policy(CITY_ID[city_A], CITY_ID[city_B]))


'''

 定时更新 & 定时推送

'''
FOCUS = DL.data

scheduler = require('nonebot_plugin_apscheduler').scheduler


@scheduler.scheduled_job('cron', minute='*/30', second='0', misfire_grace_time=60)
async def update():
    if NewsBot.update_data():
        logger.info(f"[疫情数据更新]{NewsBot.time}")
        city_list = []  # 记录推送city, 推送成功后 设置 isUpdated 为 False

        bot = get_bot()
        groups = await bot.get_group_list()
        group_id = [group['group_id'] for group in groups]
        for gid in FOCUS.keys():

            for c in FOCUS.get(gid):
                city = NewsBot.data.get(c)
                city_list.append(city)

                # 判定是否为更新后信息
                if city.isUpdated is True:
                    # send group or private
                    if int(gid) in group_id:
                        await get_bot().send_group_msg(group_id=int(gid), message='关注城市疫情变化\n' + city.main_info)
                    else:
                        await get_bot().send_private_msg(user_id=int(gid), message='关注城市疫情变化\n' + city.main_info)

        for city in city_list:
            city.isUpdated = False


'''

  高增长地区提醒推送

'''
try:
    if (getattr(get_driver().config, 'covid19', None)):
        convid_config = get_driver().config.covid19
        if convid_config.get('notice') in ['true', "True"]:
            async def notice():
                res = []
                filter_city = convid_config.get('filter', []) + ['香港', '台湾', '中国']
                for _, city in list(NewsBot.data.items()):
                    if city.all_add >= convid_config.get('red-line', 100):
                        if city.name not in filter_city:
                            res.append(f"{city.main_info}")

                if res:
                    bot = get_bot()
                    message = NewsBot.time + '\n' + '\n\n'.join(res)

                    group_list = convid_config.get('group')
                    if group_list == 'all':
                        group = await bot.get_group_list()
                        group_list = [g['group_id'] for g in group]

                    for gid in group_list:
                        await send_forward_msg_group(bot, group_id=gid, message=message)


            scheduler.add_job(notice, "cron", hour="11", minute="5", id="covid19_notice")
except Exception as e:
    logger.info(f"疫情config设置有误: {e}")

