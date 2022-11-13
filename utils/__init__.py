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
from . import database_mysql, url, users
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot import on_command, get_driver
from content.plugins import credit, plugin_control, word_cloud, sign
from .path import *
from .other import mk
from .users import superuser, Van


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
    if not os.path.exists(re_wordcloud_img_path):
        await mk("dir", re_wordcloud_img_path, mode=None)
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
    if not os.path.exists(enable_path):
        await mk("dir", enable_path, mode=None)
    if not fortune_out_path.exists():
        fortune_out_path.mkdir(exist_ok=True, parents=True)
    if not torment_path.exists():
        torment_path.mkdir(exist_ok=True, parents=True)
    if not reboot_path.exists():
        reboot_path.mkdir(exist_ok=True, parents=True)
    if not schedule_path.exists():
        schedule_path.mkdir(exist_ok=True, parents=True)
    if not leave_base_path.exists():
        leave_base_path.mkdir(exist_ok=True, parents=True)
    if not (config_path / "friends_request").exists():
        (config_path / "friends_request").mkdir(exist_ok=True, parents=True)
    if not auto_baned_path.exists():
        auto_baned_path.mkdir(exist_ok=True, parents=True)
    if not memes_path.exists():
        memes_path.mkdir(exist_ok=True, parents=True)
    if not memes_res_path.exists():
        memes_res_path.mkdir(exist_ok=True, parents=True)
    if not petpet_path.exists():
        petpet_path.mkdir(exist_ok=True, parents=True)
    if not petpet_res_path.exists():
        petpet_res_path.mkdir(exist_ok=True, parents=True)
    if not what2eat_path.exists():
        what2eat_path.mkdir(parents=True, exist_ok=True)
    if not curfew_path.exists():
        curfew_path.mkdir(parents=True, exist_ok=True)
    if not word_list_urls.exists():
        word_list_urls.mkdir(parents=True, exist_ok=True)
    # 目录初始化结束
    # 文件初始化开始
    if not os.path.exists(translate_path):
        await mk("file", translate_path, 'w', url=url.translate_json, dec="翻译文件")
    if not os.path.exists(total_unable):
        await mk("file", total_unable, 'w', url=url.unable_txt, dec="不统计插件列表")
    if not os.path.exists(epicFree_path / "status.json"):
        await mk("file", epicFree_path / "status.json", 'w', content=json.dumps({"群聊": [], "私聊": []}))
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
    if not os.path.exists(enable_config_path):
        await mk("file", enable_config_path, 'w', content=json.dumps({}))
    if not os.path.exists(torment_config_path):
        await mk("file", torment_config_path, 'w', content=json.dumps({}))
    if not os.path.exists(reboot_config_path):
        await mk("file", reboot_config_path, 'w', content=json.dumps({"rebooting": False, "gid": ""}))
    if not os.path.exists(friends_request_info):
        await mk("file", friends_request_info, 'w', content=json.dumps({}))


@driver.on_startup
async def _():
    await Dir_init()
    database_mysql.Database_init()


async def init(bot: Bot, event: GroupMessageEvent):
    # 用户表初始化开始
    gid = str(event.group_id)
    members = await bot.get_group_member_list(group_id=int(gid))
    cursor.execute(f"SELECT * FROM users WHERE gid='{gid}';")
    query: tuple = cursor.fetchall()
    month = time.strftime(fts, time.localtime())
    # 不存在数据
    if not query:
        await users.user_init_all(members)

    # 未添加至数据库的成员处理
    members_database = users.get_members_uid_by_gid(gid)
    for member in members:
        if str(member['user_id']) not in members_database:
            await users.user_init_one(gid, str(member['user_id']), member['role'])

    # 根超级用户处理
    SUPERUSERS = get_driver().config.superusers
    for superuser in SUPERUSERS:
        cursor.execute(f"UPDATE users SET role='Van' WHERE uid='{superuser}'")

    # 清除过期根用户
    superusers_database = users.get_all_Van_in_database()
    for superuser in superusers_database:
        if users.get_role(gid, superuser[1]) == "Van" and superuser[1] not in SUPERUSERS:
            users.update_role(superuser[0], superuser[1], "member")

    # 用户表初始化结束
    # 目录初始化
    await Dir_init()
    if not (word_list_urls / gid).exists():
        (word_list_urls / gid).mkdir(parents=True, exist_ok=True)
    if not (curfew_path / gid).exists():
        (curfew_path / gid).mkdir(parents=True, exist_ok=True)
    # 文件初始化
    if not os.path.exists(total_base / month / f"{gid}.json"):
        await mk("file", total_base / month / f"{gid}.json", 'w', content=json.dumps({}))
    if not os.path.exists(question_base / f"{gid}.json"):
        await mk("file", question_base / f"{gid}.json", 'w', content=json.dumps({"vague": {}, "absolute": {}}))
    if not os.path.exists(permission_special_base / f"{gid}.json"):
        await mk("file", permission_special_base / f"{gid}.json", 'w', url=url.permission_special_json, dec="特殊权限插件列表")
    if not os.path.exists(permission_common_base / f"{gid}.json"):
        await mk("file", permission_common_base / f"{gid}.json", 'w', url=url.permission_common_json, dec="常规权限插件列表")
    if not os.path.exists(demerit_path / gid):
        await mk("dir", demerit_path / gid, mode=None)
    if not os.path.exists(demerit_path / gid / f"data.json"):
        await mk("file", demerit_path / gid / f"data.json", 'w', content=json.dumps({}))
    if not os.path.exists(demerit_path / gid / f"config.json"):
        await mk("file", demerit_path / gid / f"config.json", 'w', content=json.dumps({"limit": 5}))
    if not os.path.exists(auto_baned_path / gid):
        await mk("dir", auto_baned_path / gid, mode=None)
    if not os.path.exists(auto_baned_path / gid / "time.json"):
        await mk("file", auto_baned_path / gid / "time.json", 'w', content=json.dumps({}))
    if not os.path.exists(auto_baned_path / gid / "baned.json"):
        await mk("file", auto_baned_path / gid / "baned.json", 'w', content=json.dumps({}))
    if not os.path.exists(curfew_path / gid / "config.json"):
        await mk("file", curfew_path / gid / "config.json", 'w', content=json.dumps(
            {"switch": False,
             "time":
                 {"start_hour": 23,
                  "start_minute": 0,
                  "stop_hour": 6,
                  "stop_minute": 0}
             }))
    if not os.path.exists(word_list_urls / gid / "words.txt"):
        await mk("file", word_list_urls / gid / "words.txt", 'w', content="")
    if not os.path.exists(level_path):
        await mk("file", level_path / gid / "words.txt", 'w', content=json.dumps({gid: "easy"}))
    if not os.path.exists(word_path):
        await mk("file", word_path, "w", content='123456789\n')
    if not os.path.exists(limit_word_path_easy):
        await mk("file", limit_word_path_easy, "w",
                 url="https://public-cdn-shanghai.oss-cn-shanghai.aliyuncs.com/nonebot/f_word_easy",
                 dec="简单违禁词词库")
    if not os.path.exists(welcome_path_base / f"{gid}.txt"):
        await mk("file", welcome_path_base / f"{gid}.txt", "w", content="欢迎入群")
    if not os.path.exists(back_path_base / f"{gid}.txt"):
        await mk("file", back_path_base / f"{gid}.txt", "w", content="欢迎回归")

    if not os.path.exists(limit_word_path):
        await mk("file", limit_word_path, "w",
                 url="https://public-cdn-shanghai.oss-cn-shanghai.aliyuncs.com/nonebot/f_word_s",
                 dec="严格违禁词词库")

bot_init = on_command(cmd="初始化", aliases={"机器人初始化"}, priority=1, permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER | Van | superuser)
@bot_init.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        # 各插件初始化
        gid = str(event.group_id)
        await init(bot, event)
        await credit.tools.init(bot, event)
        await plugin_control.init(gid)
        await sign.tools.init(bot, event)
        await bot_init.send("初始化成功,该项目完全免费,如果你是付费获得的，请立即退款并举报")
    # 初始化异常
    except Exception as e:
        print(str(e))
        await bot_init.send("初始化出错:" + str(e))
