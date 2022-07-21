"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/31 20:08
"""
import datetime

from utils import database_mysql
from nonebot import logger
from threading import Timer
from content.plugins.permission import tools


ftr: str = "%Y-%m-%d"
cursor = database_mysql.cursor
db = database_mysql.connect


def get_role(gid: str, uid: str) -> str:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND gid='{gid}'")
    re = cursor.fetchone()
    if re:
        return re[0]


def get_role_nogid(uid: str) -> str:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND alive=TRUE")
    re = cursor.fetchall()
    levels = []
    for r in re:
        levels.append(tools.get_lev(r[0]))
    role = tools.get_role(max(levels))
    return role


def update_role(gid: str, uid: str, role: str) -> bool:
    try:
        cursor.execute(f"UPDATE users SET role='{role}' WHERE uid='{uid}' AND gid='{gid}';")
    except:
        return False
    logger.info(f"更新用户 {uid} 权限 {role}")
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
    count = cursor.fetchone()
    if count:
        return count[0]
    else:
        return 0


def member_leave(uid, gid):
    sql = f"UPDATE users SET alive=FALSE WHERE uid='{uid}' and gid='{gid}'"
    if tools.permission_(get_role(gid, uid), "superuser"):
        sql = f"UPDATE users SET role='member',alive=FALSE WHERE uid='{uid}' and gid='{gid}'"
    cursor.execute(sql)


def get_alive(uid: str, gid: str) -> bool:
    cursor.execute(f"SELECT alive FROM users WHERE gid='{gid}' and uid='{uid}';")
    re = cursor.fetchone()
    if re:
        return re[0]
    else:
        return False


def is_member(uid: str) -> bool:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND role='member';")
    re = cursor.fetchone()
    if re:
        return True
    else:
        return False


def is_superuser(uid: str) -> bool:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND role='superuser';")
    re = cursor.fetchone()
    if re:
        return True
    else:
        return False


def is_admin(uid: str) -> bool:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND role='admin';")
    re = cursor.fetchone()
    if re:
        return True
    else:
        return False


def is_owner(uid: str) -> bool:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND role='owner';")
    re = cursor.fetchone()
    if re:
        return True
    else:
        return False


def is_Van(uid: str) -> bool:
    cursor.execute(f"SELECT role FROM users WHERE uid='{uid}' AND role='Van';")
    re = cursor.fetchone()
    if re:
        return True
    else:
        return False
