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


async def init(bot: Bot, event: GroupMessageEvent):
    members = await bot.call_api(api="get_group_member_list", group_id=event.group_id)
    date_now = datetime.datetime.now()
    date_pre: str = datetime.datetime.strftime(date_now - datetime.timedelta(days=1), ftr)    # 查询用户语句
    sql_query: str = f'''SELECT * FROM sign'''
    cursor.execute(sql_query)
    db.commit()
    result_query: tuple = cursor.fetchall()
    added: list = []
    # 查找新用户
    if result_query:
        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])
            for re in result_query:
                if gid == re[0] and uid == re[1]:
                    added.append([gid, uid])
                    break

    # 首次创建
    else:
        for member in members:
            uid = member['user_id']
            gid = member['group_id']
            sql_insert = f"INSERT INTO sign VALUES ('{gid}','{uid}','{date_pre}',0,0)"
            cursor.execute(sql_insert)
            db.commit()
        return

    # 添加新用户
    for member in members:
        gid = str(member['group_id'])
        uid = str(member['user_id'])
        if [gid, uid] not in added:
            sql_insert = f"INSERT INTO sign VALUES ('{gid}','{uid}','{date_pre}',0,0)"
            cursor.execute(sql_insert)
            db.commit()
