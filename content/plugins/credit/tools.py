"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/26 15:40
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot

from utils import database_mysql


cursor = database_mysql.cursor
db = database_mysql.connect


# 初始化函数
async def init(bot: Bot, event: GroupMessageEvent):
    # 积分表初始化开始
    members = await bot.call_api(api="get_group_member_list", group_id=event.group_id)
    cursor.execute("SELECT * FROM credit;")
    db.commit()
    query: tuple = cursor.fetchall()
    # 已存在数据
    if query:
        l: list = []
        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])

            for re in query:
                if re[0] == gid and re[1] == uid:
                    l.append([gid, uid])

        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])
            if [gid, uid] not in l:
                cursor.execute(f"INSERT INTO credit VALUES('{gid}', '{uid}', 0);")
                db.commit()
    # 第一次添加
    else:
        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])
            cursor.execute(f"INSERT INTO credit VALUES('{gid}', '{uid}', 0);")
        db.commit()
    # 积分表初始化结束


# 增加积分
def add(gid: str, uid: str, credit: int):
    cursor.execute(f"SELECT credit FROM credit WHERE uid='{uid}' and gid='{gid}';")
    credit_old = cursor.fetchone()[0]
    cursor.execute(f"UPDATE credit SET credit={credit + credit_old} WHERE gid='{gid}' and uid='{uid}';")
    db.commit()


# 减少积分
def minus(gid: str, uid: str, credit: int):
    cursor.execute(f"SELECT credit FROM credit WHERE uid='{uid}' and gid='{gid}';")
    credit_old = cursor.fetchone()[0]
    credit = credit_old - credit
    if credit < 0:
        credit = 0
    cursor.execute(f"UPDATE credit SET credit={credit} WHERE gid='{gid}' and uid='{uid}';")
    db.commit()


# 积分累加函数
def added(num: int, add: int) -> int:
    if 5 <= add < 10:
        return num + 5
    elif 10 <= add < 15:
        return num + 10
    elif 15 <= add < 20:
        return num + 20
    elif 20 <= add < 30:
        return num + 30
    elif add >= 30:
        return num + 40
    return num


# 排行榜(最多)
async def top(gid: str, bot: Bot) -> str:
    message: str = "总积分排行榜(前10),名字:积分\n"
    cursor.execute(f"SELECT credit.uid, credit FROM credit LEFT JOIN users ON credit.uid=users.uid AND credit.gid=users.gid WHERE alive=1 AND credit.gid='{gid}' ORDER BY credit DESC LIMIT 10;")
    query = cursor.fetchall()
    a = 1
    for re in query:
        uid = re[0]
        credit = re[1]
        info = await bot.call_api(api="get_group_member_info", group_id=int(gid), user_id=int(uid))
        nickname = info['nickname']
        message += f"{a}.{nickname}:{credit}\n"
        a += 1
    return message


# 获取积分
async def get(gid: int, uid: int) -> str:
    cursor.execute(f"SELECT credit FROM credit WHERE gid='{gid}' and uid='{uid}';")
    return str(cursor.fetchone()[0])
