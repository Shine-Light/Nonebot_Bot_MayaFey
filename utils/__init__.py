"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/23 12:46
"""
import json
import os
import time

import requests
from nonebot.permission import SUPERUSER
from . import database_mysql
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot import on_command, get_driver
from content.plugins import credit, plugin_control, ban_word, word_cloud, welcome, sign
from .path import *
from .other import mk
from . import hook, url

db = database_mysql.connect
cursor = database_mysql.cursor
fts = "%Y-%m"
driver = get_driver()


async def Dir_init():
    month = time.strftime(fts, time.localtime())

    # 目录初始化开始
    if not os.path.exists(config_path):
        await mk("dir", config_path, mode=None)
    if not os.path.exists(res_path):
        await mk("dir", res_path, mode=None)
    if not os.path.exists(font_path):
        await mk("dir", font_path, mode=None)
    if not os.path.exists(txt_path):
        await mk("dir", txt_path, mode=None)
    if not os.path.exists(audio_path):
        await mk("dir", audio_path, mode=None)
    if not os.path.exists(video_path):
        await mk("dir", video_path, mode=None)
    if not os.path.exists(img_path):
        await mk("dir", img_path, mode=None)

    if not os.path.exists(admin_path):
        await mk("dir", admin_path, mode=None)
    if not os.path.exists(words_contents_path):
        await mk("dir", words_contents_path, mode=None)
    if not os.path.exists(re_wordcloud_path):
        await mk("dir", re_wordcloud_path, mode=None)
    if not os.path.exists(re_img_path):
        await mk("dir", re_img_path, mode=None)
    if not os.path.exists(wordcloud_bg_path):
        await mk("dir", wordcloud_bg_path, mode=None)
    if not os.path.exists(group_message_data_path):
        await mk("dir", group_message_data_path, mode=None)
    if not os.path.exists(welcome_path_base):
        await mk("dir", welcome_path_base, mode=None)
    if not os.path.exists(back_path_base):
        await mk("dir", back_path_base, mode=None)
    if not os.path.exists(total_base):
        await mk("dir", total_base, mode=None)
    if not os.path.exists(total_base / month):
        await mk("dir", total_base / month, mode=None)
    if not os.path.exists(question_base):
        await mk("dir", question_base, mode=None)
    if not os.path.exists(permission_base):
        await mk("dir", permission_base, mode=None)
    if not os.path.exists(permission_common_base):
        await mk("dir", permission_common_base, mode=None)
    if not os.path.exists(permission_special_base):
        await mk("dir", permission_special_base, mode=None)
    if not os.path.exists(update_cfg_path):
        await mk("dir", update_cfg_path, mode=None)
    if not os.path.exists(epicFree_path):
        await mk("dir", epicFree_path, mode=None)
    if not os.path.exists(morning_path):
        await mk("dir", morning_path, mode=None)
    if not os.path.exists(config_path / "fortune"):
        await mk("dir", config_path / "fortune", mode=None)
    if not os.path.exists(demerit_path):
        await mk("dir", demerit_path, mode=None)
    # 目录初始化结束





@driver.on_startup
async def _():
    await Dir_init()
    database_mysql.Database_init()


async def init(bot: Bot, event: GroupMessageEvent):
    # 用户表初始化开始
    members = await bot.call_api(api="get_group_member_list", group_id=event.group_id)
    cursor.execute(f"SELECT * FROM users WHERE gid='{event.group_id}';")
    query: tuple = cursor.fetchall()
    month = time.strftime(fts, time.localtime())
    # 已存在数据
    if query:
        l: list = []
        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])

            for re in query:
                # 已在群内
                if re[0] == gid and re[1] == uid:
                    l.append([gid, uid])

        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])
            if [gid, uid] not in l:
                role = member['role']
                cursor.execute(f"INSERT INTO users VALUES('{gid}','{uid}','{role}',0,TRUE);")
                db.commit()

    # 第一次添加
    else:
        for member in members:
            gid = str(member['group_id'])
            uid = str(member['user_id'])
            role = member['role']
            cursor.execute(f"INSERT INTO users VALUES('{gid}', '{uid}', '{role}', 0, TRUE);")
            db.commit()

    # 根超级用户处理
    SUPERUSERS = get_driver().config.superusers
    for superuser in SUPERUSERS:
        cursor.execute(f"UPDATE users SET role='Van' WHERE uid='{superuser}'")

    # 用户表初始化结束
    # 目录初始化
    await Dir_init()
    # 文件初始化
    gid = str(event.group_id)
    if not os.path.exists(translate_path):
        await mk("file", translate_path, 'w', url=url.translate_json, dec="翻译文件")
    if not os.path.exists(total_base / month / f"{gid}.json"):
        await mk("file", total_base / month / f"{gid}.json", 'w', content=json.dumps({}))
    if not os.path.exists(total_unable):
        await mk("file", total_unable, 'w', url=url.unable_txt, dec="不统计插件列表")
    if not os.path.exists(question_base / f"{gid}.json"):
        await mk("file", question_base / f"{gid}.json", 'w', content=json.dumps({}))
    if not os.path.exists(permission_special_base / f"{gid}.json"):
        await mk("file", permission_special_base / f"{gid}.json", 'w', url=url.permission_special_json, dec="特殊权限插件列表")
    if not os.path.exists(permission_common_base / f"{gid}.json"):
        await mk("file", permission_common_base / f"{gid}.json", 'w', url=url.permission_common_json, dec="常规权限插件列表")
    if not os.path.exists(updating_path):
        await mk("file", updating_path, 'w', content=json.dumps({"updating": False}))
    if not os.path.exists(unset_path):
        await mk("file", unset_path, 'w', url=url.unset_txt, dec="不可设置插件列表")
    if not os.path.exists(version_path):
        await mk("file", version_path, 'w', content=requests.get(url.version_html).text)
    if not os.path.exists(morning_config_path):
        await mk("file", morning_config_path, 'w', url=url.morning_config, dec="早安插件配置文件")
    if not os.path.exists(morning_data_path):
        await mk("file", morning_data_path, 'w', content=json.dumps({}))
    if not os.path.exists(fortune_config_path):
        await mk("file", fortune_config_path, 'w', content=json.dumps({}))
    if not os.path.exists(epicFree_path / "status.json"):
        await mk("file", epicFree_path / "status.json", 'w', content=json.dumps({"群聊": [], "私聊": []}))
    if not os.path.exists(demerit_path / gid):
        await mk("dir", demerit_path / gid, mode=None)
    if not os.path.exists(demerit_path / gid / f"data.json"):
        await mk("file", demerit_path / gid / f"data.json", 'w', content=json.dumps({}))
    if not os.path.exists(demerit_path / gid / f"config.json"):
        await mk("file", demerit_path / gid / f"config.json", 'w', content=json.dumps({"limit": 5}))

bot_init = on_command(cmd="初始化", aliases={"机器人初始化"}, priority=1, permission=GROUP_OWNER | GROUP_ADMIN |SUPERUSER)
@bot_init.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        # 各插件初始化
        gid = str(event.group_id)
        await init(bot, event)
        await credit.tools.init(bot, event)
        await plugin_control.init(gid)
        await ban_word.init(gid)
        await sign.tools.init(bot, event)
        await word_cloud.tools.init()
        await welcome.tools.init(gid)
        await bot_init.send("初始化成功,该项目完全免费,如果你是收费获得的，请立即退款并举报")
    # 初始化异常
    except Exception as e:
        await bot_init.send("初始化出错:" + str(e))
