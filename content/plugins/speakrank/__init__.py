"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/4 21:58
"""
import datetime
import os


from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from utils.path import group_message_data_path
from utils.admin_tools import At, load, upload


# FIXME: 这一块重复代码有点多了
who_speak_most_today = on_command("今日榜首", aliases={'今天谁话多', '今儿谁话多', '今天谁屁话最多'}, block=True, priority=8)
@who_speak_most_today.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    today = datetime.date.today().strftime("%Y-%m-%d")
    dic_ = await load(group_message_data_path/f"{gid}" / f"{today}.json")
    top = sorted(dic_.items(), key=lambda x: x[1], reverse=True)
    if len(top) == 0:
        await who_speak_most_today.send("没有任何人说话")
        return
    else:
        await who_speak_most_today.send(f"太强了！今日榜首：\n{top[0][0]}，发了{top[0][1]}条消息")


speak_top = on_command("今日发言排行", aliases={'今日排行榜', '今日发言排行榜', '今日排行'}, block=True, priority=8)
@speak_top.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    today = datetime.date.today().strftime("%Y-%m-%d")
    dic_ = await load(group_message_data_path/f"{gid}" / f"{today}.json")
    top = sorted(dic_.items(), key=lambda x: x[1], reverse=True)
    if len(top) == 0:
        await speak_top.send("没有任何人说话")
        return
    top_list = []
    for i in range(min(len(top), 10)):
        top_list.append(f"{i+1}. {top[i][0]}，发了{top[i][1]}条消息")
    await speak_top.send("\n".join(top_list))


speak_top_yesterday = on_command("昨日发言排行", aliases={'昨日排行榜', '昨日发言排行榜', '昨日排行'}, block=True, priority=8)
@speak_top_yesterday.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if os.path.exists(group_message_data_path/f"{gid}" / f"{yesterday}.json"):
        dic_ = await load(group_message_data_path/f"{gid}" / f"{yesterday}.json")
        top = sorted(dic_.items(), key=lambda x: x[1], reverse=True)
        if len(top) == 0:
            await speak_top_yesterday.send("没有任何人说话")
            return
        top_list = []
        for i in range(min(len(top), 10)):
            top_list.append(f"{i+1}. {top[i][0]}，发了{top[i][1]}条消息")
        await speak_top_yesterday.send("\n".join(top_list))
    else:
        await speak_top_yesterday.send("昨日没有记录")


who_speak_most = on_command("排行", aliases={'谁话多', '谁屁话最多', '排行', '排行榜'}, block=True, priority=8)
@who_speak_most.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    dic_ = await load(group_message_data_path / f"{gid}" / "history.json")
    top = sorted(dic_.items(), key=lambda x: x[1], reverse=True)
    if len(top) == 0:
        await who_speak_most.send("没有任何人说话")
        return
    else:
        top_list = []
        for i in range(min(len(top), 10)):
            top_list.append(f"{i+1}. {top[i][0]}，发了{top[i][1]}条消息")
        await who_speak_most.send("\n".join(top_list))


get_speak_num = on_command("发言数", aliases={'发言数', '发言', '发言量'}, block=True, priority=8)
@get_speak_num.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    dic_ = await load(group_message_data_path / f"{gid}" / "history.json")
    at_list = At(event.json())
    if at_list:
        for qq in at_list:
            qq = str(qq)
            if qq in dic_:
                await get_speak_num.send(f"有记录以来{qq}在本群发了{dic_[qq]}条消息")
            else:
                await get_speak_num.send(f"{qq}没有发消息")


get_speak_num_today = on_command("今日发言数", aliases={'今日发言数', '今日发言', '今日发言量'}, block=True, priority=8)
@get_speak_num_today.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    today = datetime.date.today().strftime("%Y-%m-%d")
    dic_ = await load(group_message_data_path / f"{gid}" / f"{today}.json")
    at_list = At(event.json())
    if at_list:
        for qq in at_list:
            qq = str(qq)
            if qq in dic_:
                await get_speak_num_today.send(f"今天{qq}发了{dic_[qq]}条消息")
            else:
                await get_speak_num_today.send(f"今天{qq}没有发消息")