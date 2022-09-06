"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/6 17:15
"""
from nonebot import on_command, require, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from nonebot.plugin import PluginMetadata


from .tools import *
from utils import json_tools
from utils.path import *
from utils import database_mysql
from .. import permission
from utils import users
from utils.other import add_target, translate


ban_count_allow = get_driver().config.ban_count_allow
custom_ban_msg = f'''
说明: 违禁词有两套系统,一套自定义系统,一套内置系统
     超级用户及以上不会被违禁词系统处罚
     两者违禁词不可重复,如需将关键词处罚力度提高至自定义系统等级请使用强制添加
     内置系统违禁词为侮辱性词汇及其他敏感词汇,处罚永久为禁言5min
     自定义系统处罚为:第1次禁言 30min,第2次禁言 0.5day,第N次禁言1day,第{ban_count_allow}次踢出并拉黑
[群员及以上]
查看违禁词:违禁词 列表
[超管及以上]
增删违禁词,可以批量添加和删除,用"|"分隔,内容可带空格
添加违禁词:/违禁词 + {{内容}}
删除违禁词:/违禁词 - {{内容}}
强制添加违禁词:/违禁词 ++ {{内容}}
'''.strip()


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "ban_word"),
    description="自动检测违禁词并撤回",
    usage=custom_ban_msg + add_target(60)
)


cursor = database_mysql.cursor
time_now = ""
config_url = config_path
word_list_message = "以下是违禁词列表,侮辱性或其他敏感词汇已内置,无须再添加:\n"
preBanWord = limit_word_path
preBanWord_easy = limit_word_path_easy


# 增删查
baned = on_command(cmd="违禁词", priority=8)
@baned.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    uid = str(event.group_id)
    group_id = str(event.group_id)
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "baned", gid):
        word_list_url = word_list_urls / group_id / "words.txt"

        # 简单信息处理
        msg_meta: str = str(event.get_message())
        place: list = msg_meta.split(" ", 2)

        # 命令小于2段
        if len(place) < 2:
            await baned.finish(message="命令有误")

        # 命令2段代码
        elif len(place) == 2:
            # 获取模式
            mode: str = place[1]
            # 列表模式
            if mode == "列表":
                msgs: str = ""
                # 遍历列表
                with open(word_list_url, "r", encoding="utf-8") as wordlist:
                    # 列表为空
                    if wordlist.read() == "":
                        await baned.finish(message="未设置违禁词")
                # 遍历词汇
                for word in open(word_list_url, "r", encoding="utf-8"):
                    # 去除词汇换行
                    msg = word.replace("\n", "")
                    msgs += f"{msg},"
                await baned.finish(message=word_list_message + msgs[:-1] + add_target(30))

            elif mode == "帮助":
                await baned.finish(message=custom_ban_msg)

            elif mode == "清空":
                # 成员无权限清空
                role = users.get_role(group_id, uid)
                if permission.tools.permission_(role, "superuser"):
                    await baned.finish(message="无权限" + add_target(30))
                file = open(word_list_url, "w+", encoding="utf-8")
                file.close()
                await baned.finish(message="已清空")

            # 没有指定的模式
            else:
                await baned.finish(message="命令有误")

        # 命令3段代码
        elif len(place) == 3:
            # 成员无权限添加/删除
            role = users.get_role(group_id, uid)
            if permission.tools.permission_(role, "superuser"):
                await baned.finish(message="无权限" + add_target(30))

            # 获取模式和内容
            mode: str = place[1]
            content: str = place[2]
            # 获取关键词
            words_in: list = content.split("|")

            # 追加模式
            if mode == "+":
                having_pre: list = []
                having_preEasy: list = []
                having_custom: list = []
                msg = "添加成功"
                for keyword in words_in:
                    writing: bool = True
                    # 已存在内置字典的词汇不添加
                    if "\n" + keyword + "\n" in open(preBanWord, "r", encoding="utf-8").read():
                        having_pre.append(keyword)
                        writing = False
                    if "\n" + keyword + "\n" in open(preBanWord_easy, "r", encoding="utf-8").read():
                        having_preEasy.append(keyword)
                        writing = False
                    # 已添加的词汇不再添加(第一行)
                    if keyword + "\n" in open(word_list_url, encoding="utf-8").read():
                        # 判断元素是否为空格后的最后一个元素
                        if keyword + "\n" == open(word_list_url, "r", encoding="utf-8").readline():
                            having_custom.append(keyword)
                            writing = False
                    # 已添加的词汇不再添加(其他行)
                    if "\n" + keyword + "\n" in open(word_list_url, encoding="utf-8").read():
                        having_custom.append(keyword)
                        writing = False

                    # 若关键词不存在
                    if writing:
                        # 写入关键词
                        with open(word_list_url, "a", encoding="utf-8") as words:
                            words.write(keyword + "\n")

                if len(having_custom) == 0 and len(having_pre) == 0 and len(having_preEasy) == 0:
                    await baned.finish(message=msg + add_target(30))

                # 批量添加失败信息
                else:
                    msg_pre = "以下词汇添加失败\n"
                    msg_total = ""
                    msg1 = ""
                    msg2 = ""
                    msg3 = ""
                    if len(having_pre) > 0:
                        for pre in having_pre:
                            msg1 += pre + ","
                        msg1 = "这些词汇存在于内置严格字典:" + "\n" + msg1
                        msg_total += msg1
                    if len(having_preEasy) > 0:
                        for pre in having_preEasy:
                            msg2 += pre + ","
                        msg2 = "这些词汇存在于内置简单字典:" + "\n" + msg2
                        msg_total += msg2
                    if len(having_custom) > 0:
                        for pre in having_custom:
                            msg3 += pre + ","
                        msg3 = "这些词汇存在于自定义字典:" + "\n" + msg3
                        msg_total += msg3
                    await baned.finish(message=msg_pre + msg_total + add_target(60))

            # 强制增加模式
            if mode == "++":
                having_custom: list = []
                msg = "添加成功"
                for keyword in words_in:
                    writing: bool = True
                    # 已添加的词汇不再添加(第一行)
                    if keyword + "\n" in open(word_list_url, encoding="utf-8").read():
                        # 判断元素是否为空格后的最后一个元素
                        if keyword + "\n" == open(word_list_url, "r", encoding="utf-8").readline():
                            having_custom.append(keyword)
                            writing = False
                    # 已添加的词汇不再添加(其他行)
                    if "\n" + keyword + "\n" in open(word_list_url, encoding="utf-8").read():
                        having_custom.append(keyword)
                        writing = False

                    # 若关键词不存在
                    if writing:
                        # 写入关键词
                        with open(word_list_url, "a", encoding="utf-8") as words:
                            words.write(keyword + "\n")

                # 全部添加成功
                if len(having_custom) == 0:
                    await baned.finish(message=msg)

                # 批量添加失败信息
                else:
                    msg_pre = "以下词汇添加失败:\n"
                    msg_total = ""
                    msg1 = ""
                    if len(having_custom) > 0:
                        for pre in having_custom:
                            msg1 += pre + ","
                        msg1 = "这些词汇存在于自定义字典:" + msg1[:-1] + "\n"
                        msg_total += msg1
                    await baned.finish(message=msg_pre + msg_total + add_target(60))

            # 删减模式
            if mode == "-":
                NoExist: list = []
                for keyword in words_in:
                    deleteing: bool = True
                    # 词汇不存在
                    if keyword + "\n" not in open(word_list_url, "r", encoding="utf-8").read():
                        NoExist.append(keyword)
                        deleteing = False

                    # 若词汇存在,则开始删除
                    if deleteing:
                        line = 1
                        for c in open(word_list_url, "r", encoding="utf-8"):
                            if c == keyword + "\n":
                                break
                            else:
                                line += 1
                        word_out: str = ""
                        with open(word_list_url, "r", encoding="utf-8") as file:
                            words: list = file.readlines()
                            index = line - 1
                            words.pop(index)
                            for word in words:
                                word_out += word
                            file.close()
                        file = open(word_list_url, "w", encoding="utf-8")
                        file.write(word_out)
                        file.close()

                if len(NoExist) == 0:
                    await baned.finish(message="删除成功")
                else:
                    msg = "以下词汇不存在:\n"
                    for keyword in NoExist:
                        msg += keyword + ","
                    msg = msg[:-1]
                    await baned.finish(message=msg)

    else:
        await baned.send("无权限")


# 违禁词检测
@event_preprocessor
async def _(event: GroupMessageEvent, bot: Bot):
    if "启用" in event.get_plaintext() or "停用" in event.get_plaintext():
        return
    if "初始化" in event.get_plaintext():
        return
    # 是否为增删指令
    msg_meta: str = event.get_message().extract_plain_text()
    msgs = msg_meta.split(" ", 2)
    if len(msgs) >= 2:
        if (msgs[1] == "++" or msgs[1] == "+" or msgs[1] == "-") and event.sender.role != "member":
            return
    # 初始化设置
    group_id = str(event.group_id)
    uid = event.get_user_id()
    word_list_url = word_list_urls / group_id / "words.txt"
    msg_meta = event.get_message().extract_plain_text()
    role: str = users.get_role(group_id, uid)
    ban_words: list = open(word_list_url, "r", encoding="utf-8").read().split("\n")
    preBanWords: list = open(preBanWord, "r", encoding="utf-8").read().split("\n")
    preBanWords_easy: list = open(preBanWord_easy, "r", encoding="utf-8").read().split("\n")
    level = json.loads(open(level_path, 'r', encoding='utf-8').read())[group_id]
    # 检测是否触发关键词(自定义违禁词)
    for word in ban_words:
        if word and word in msg_meta:
            if not permission.tools.permission_(role, "superuser"):
                await ban_count(uid, str(group_id))
                count = users.get_ban_count(uid, group_id)
                if count == 1:
                    times = "30min"
                elif count == 2:
                    times = "0.5day"
                else:
                    times = "1day"
                # 第n次踢出并拉黑
                if count >= ban_count_allow:
                    try:
                        await kick_user(uid, group_id, bot)
                    except:
                        await bot.send(event=event, message="检测到违禁词,无管理员权限,无法进行处罚")
                        IgnoredException("触发违禁词")
                    await bot.send(event=event, message=f"检测到违禁词,次数已达{ban_count_allow}次,踢出并拉黑")
                    IgnoredException("触发违禁词")
                else:
                    try:
                        await ban_user(uid, group_id, bot)
                    except:
                        await bot.send(event=event, message="无管理员权限,无法进行处罚")
                        raise IgnoredException("触发违禁词")
                    await bot.send(event=event, message=f"检测到违禁词,第{count}次违规,禁言{times},请注意自己的言行", at_sender=True)
                    raise IgnoredException("触发违禁词")
            # 管理员不做限制
            else:
                logger.info("超级用户及以上触发违禁词")
    # 违禁词检测(内置违禁词)
    if level == "strict":
        for word in preBanWords:
            if word and word in msg_meta:
                if role in ["member", "baned"]:
                    await bot.call_api("set_group_ban", group_id=group_id, user_id=uid, duration=300)
                    await bot.send(event=event, message=f"检测到违禁词,禁言5min,请注意自己的言行", at_sender=True)
                    logger.info("触发违禁词:" + word)
                else:
                    logger.info("超级用户及以上触发违禁词:" + word)

    elif level == "easy":
        for word in preBanWords_easy:
            if word and word in msg_meta:
                if role in ["member", "baned"]:
                    await bot.call_api("set_group_ban", group_id=group_id, user_id=uid, duration=300)
                    await bot.send(event=event, message=f"检测到违禁词,禁言5min,请注意自己的言行", at_sender=True)
                    logger.info("触发违禁词:" + word)
                else:
                    logger.info("超级用户及以上触发违禁词:" + word)

ban_easy = on_command("简单违禁词", priority=5)
@ban_easy.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "ban_easy", gid):
        level: dict = json_tools.json_load(level_path)
        level.update({gid: "easy"})
        json_tools.json_write(level_path, level)
        await ban_easy.send("设置成功")
    else:
        await ban_easy.send("无权限")


ban_strict = on_command("严格违禁词", priority=5)
@ban_strict.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "ban_strict", gid):
        level: dict = json_tools.json_load(level_path)
        level.update({gid: "strict"})
        json_tools.json_write(level_path, level)
        await ban_strict.send("设置成功")
    else:
        await ban_strict.send("无权限")


scheduler = require("nonebot_plugin_apscheduler").scheduler
# 每周一更新违禁词库
scheduler.add_job(auto_upload_f_words, 'cron', day_of_week='mon', hour=0, minute=0, second=0, id='auto_upload_f_words', timezone='Asia/Shanghai')
