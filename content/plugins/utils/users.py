"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/31 20:08
"""
import datetime

from ..utils import database_mysql
from nonebot import logger
from threading import Timer

ftr: str = "%Y-%m-%d"
cursor = database_mysql.cursor
db = database_mysql.connect


def get_role(gid: str, uid: str) -> str:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND gid='{gid}'")
    re = cursor.fetchone()
    if re:
        return re[0]


def update_role(gid: str, uid: str, role: str) -> bool:
    try:
        cursor.execute(f"UPDATE users SET role='{role}' WHERE uid='{uid}' AND gid='{gid}';")
    except:
        return False
    logger.info(f"更新用户权限 {role}")
    return True


def get_countAll(gid, uid) -> int:
    cursor.execute(f"SELECT count_all FROM sign WHERE uid='{uid}' AND gid='{gid}';")
    re = cursor.fetchone()
    if re:
        return re[0]
    return 0


def get_countContinue(gid, uid) -> int:
    cursor.execute(f"SELECT count_continue FROM sign WHERE uid='{uid}' AND gid='{gid}';")
    re = cursor.fetchone()
    if re:
        return re[0]
    return 0


def get_dateLast(gid, uid) -> str:
    cursor.execute(f"SELECT date_last FROM sign WHERE uid='{uid}' AND gid='{gid}';")
    re = cursor.fetchone()
    if re:
        return datetime.datetime.strftime(re[0], ftr)


def get_credit(gid, uid) -> int:
    cursor.execute(f"SELECT credit FROM credit LEFT JOIN users ON credit.uid=users.uid AND credit.gid=users.gid WHERE alive=1 AND credit.uid='{uid}' AND credit.gid='{gid}';")
    re = cursor.fetchone()
    if re:
        return re[0]
    else:
        return -1


def set_member_later(gid, uid, time: int):
    Timer(time + 3600, update_role, (gid, uid, 'member')).start()


def get_ban_count(uid: str, gid: str) -> int:
    cursor.execute(f"SELECT ban_count FROM users WHERE gid='{gid}' and uid='{uid}';")
    count = cursor.fetchone()[0]
    return count


def member_leave(uid, gid):
    cursor.execute(f"UPDATE users SET alive=FALSE WHERE uid='{uid}' and gid='{gid}'")
