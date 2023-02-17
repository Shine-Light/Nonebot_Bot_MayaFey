"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/7 20:49
"""
import ujson as json

from nonebot.adapters.onebot.v11 import Bot
from utils import database_mysql, json_tools, users
from utils.path import level_path, word_list_urls, limit_word_path, limit_word_path_easy

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
    await bot.call_api("set_group_kick", group_id=int(gid), user_id=int(uid), reject_add_request=True)


def get_word_list(gid: str) -> set:
    """
    获取自定义违禁词列表
    gid: 群号
    """
    word_list_url = word_list_urls / gid / "words.txt"
    with open(word_list_url, "r", encoding="utf-8") as words:
        temp = words.read()
        if not temp:
            return set()
        else:
            return set(temp.strip().split("\n"))


def get_word_pre() -> set:
    """
    获取内置严格违禁词列表
    """
    with open(limit_word_path, "r", encoding="utf-8") as words:
        temp = words.read()
        if not temp:
            return set()
        else:
            return set(temp.strip().split("\n"))


def get_word_preEasy() -> set:
    """
    获取内置简单违禁词列表
    """
    with open(limit_word_path_easy, "r", encoding="utf-8") as words:
        temp = words.read()
        if not temp:
            return set()
        else:
            return set(temp.strip().split("\n"))


def removeDuplicate(words: list) -> set:
    """
    违禁词列表去重
    words: 违禁词列表
    """
    return set(words)


def clear_words(gid: str):
    """
    清空违禁词
    gid: 群号
    """
    word_list_url = word_list_urls / gid / "words.txt"
    file = open(word_list_url, "w+", encoding="utf-8")
    file.close()


def wordsExist(gid: str, words: set) -> dict:
    """
    返回已存在的违禁词
    gid: 群号
    words: 违禁词列表
    """
    having_pre: set = set()
    having_preEasy: set = set()
    having_custom: set = set()
    temp: dict = {}
    custom_words = get_word_list(gid)
    pre_words = get_word_pre()
    preEasy_words = get_word_preEasy()
    for word in words:
        if word in custom_words:
            having_custom.add(word)
        elif word in pre_words:
            having_pre.add(word)
        elif word in preEasy_words:
            having_preEasy.add(word)
    if having_pre:
        temp.update({"having_pre": having_pre})
    if having_preEasy:
        temp.update({"having_preEasy": having_preEasy})
    if having_custom:
        temp.update({"having_custom": having_custom})
    return temp


def add_words(gid: str, words: set):
    """
    添加违禁词
    gid: 群号
    words: 违禁词列表
    """
    if not words:
        return
    word_list_url = word_list_urls / gid / "words.txt"
    with open(word_list_url, "a", encoding="utf-8") as file:
        for word in words:
            file.write(word + "\n")


def remove_words(gid: str, words: set):
    """
    删除违禁词
    gid: 群号
    words: 违禁词列表
    """
    word_list_url = word_list_urls / gid / "words.txt"
    custom_words = get_word_list(gid)
    words = (words & custom_words) ^ custom_words
    with open(word_list_url, "w+", encoding="utf-8") as file:
        file.write("\n".join(words))


def get_level(gid: str):
    """
    获取群聊内置违禁词等级
    gid: 群号
    """
    return json_tools.json_load(level_path).get(gid)


def set_level(gid: str, level: str):
    """
    设置群聊内置违禁词等级
    gid: 群号
    level: 等级
    """
    json_tools.json_update(level_path, gid, level)
