"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/7 20:49
"""
import ujson as json
import os

import httpx
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot
from utils import database_mysql, json_tools, users
from utils.path import *
from utils.other import mk

cursor = database_mysql.cursor
db = database_mysql.connect


async def init(gid: str):
    try:
        js = json_tools.json_load(level_path)
        if gid not in js:
            js.update({gid: "easy"})
            json_tools.json_write(level_path, js)
    except:
        pass


async def ban_user(uid: str, gid: str, bot: Bot):
    count = users.get_ban_count(uid, gid)
    if count == 1:
        time = 1800  # 30min
    elif count == 2:
        time = 43200  # 12h
    else:
        time = 86400  # 1day
    users.update_role(gid, uid, 'baned')
    users.set_member_later(gid, uid, time)
    await bot.call_api("set_group_ban", group_id=gid, user_id=uid, duration=time)


async def ban_count(uid: str, gid: str):
    # 查询语句
    cursor.execute(f"SELECT ban_count FROM users WHERE gid='{gid}' and uid='{uid}';")
    t = cursor.fetchone()
    count = t[0]
    count += 1
    cursor.execute(f"UPDATE users SET ban_count={count} WHERE gid='{gid}' and uid='{uid}';")


async def kick_user(uid: str, gid: str, bot: Bot):
    users.member_leave(gid, uid)
    await bot.call_api("set_group_kick", group_id=gid, user_id=uid, reject_add_request=True)


async def auto_upload_f_words():
    logger.info("自动更新严格违禁词库...")
    async with httpx.AsyncClient() as client:
        try:
            r = (await client.get(url="https://public-cdn-shanghai.oss-cn-shanghai.aliyuncs.com/nonebot/f_word_s")).text
        except Exception as err:
            logger.error(f"自动更新严格违禁词库失败：{err}")
            return True
    with open(limit_word_path, "w", encoding='utf-8') as lwp:
        lwp.write(r)
        lwp.close()
    logger.info("正在更新简单违禁词库")
    async with httpx.AsyncClient() as client:
        try:
            r = (await client.get(url="https://public-cdn-shanghai.oss-cn-shanghai.aliyuncs.com/nonebot/f_word_easy")).text
        except Exception as err:
            logger.error(f"自动更新简单违禁词库失败：{err}")
            return True
    with open(limit_word_path_easy, "w", encoding='utf-8') as lwp:
        lwp.write(r)
        lwp.close()
    logger.info("更新完成")
