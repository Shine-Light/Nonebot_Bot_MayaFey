"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/31 21:40
"""
import datetime

from utils import database_mysql
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent


# 格式化字符串
ftr: str = "%Y-%m-%d"
cursor = database_mysql.cursor
db = database_mysql.connect


async def init_one(
        gid: str,
        uid: str,
        date_pre: str = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1), ftr),
        count_all: int = 0,
        count_continue: int = 0
):
    sql_insert = f"INSERT INTO sign VALUES ('{gid}','{uid}','{date_pre}',{count_all},{count_continue})"
    cursor.execute(sql_insert)


async def init(bot: Bot, event: GroupMessageEvent):
    members = await bot.call_api(api="get_group_member_list", group_id=event.group_id)
    sql_query: str = f"SELECT * FROM sign WHERE gid='{str(event.group_id)}'"
    cursor.execute(sql_query)
    result_query: tuple = cursor.fetchall()
    # 查找新用户
    if not result_query:
        for member in members:
            uid = member['user_id']
            gid = member['group_id']
            await init_one(gid, uid)
    # 0.5.8过渡,将在下个版本删除
    else:
        for member in members:
            uid = member['user_id']
            gid = member['group_id']
            cursor.execute(f"SELECT gid, uid FROM sign WHERE gid='{gid}' AND uid='{uid}'")
            if not cursor.fetchone():
                await init_one(gid, uid)