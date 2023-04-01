"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/2/17 18:53
"""
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message
from nonebot.params import CommandArg
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from . import tools
from utils import users
from utils.permission import permission_
from utils.matcherManager import matcherManager
from utils.other import add_target
from content.plugins.plugin_control.functions import get_state


pres: set = get_driver().config.command_start
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
    name="ban_word",
    description="自动检测违禁词并撤回",
    usage=custom_ban_msg + add_target(60),
    extra={
        "generate_type": "none",
        "permission_common": "baned",
        "unset": False,
        "total_unable": True,
        "author": "Shine_Light",
        "translate": "违禁词检测",
        "permission_special": {
            "ban_word:listWord": "member",
            "ban_word:clearWord": "superuser",
            "ban_word:addWord": "superuser",
            "ban_word:addWordForce": "superuser",
            "ban_word:removeWord": "superuser",
            "ban_word:easyLevel": "superuser",
            "ban_word:strictLevel": "superuser",
            "ban_word:noneLevel": "superuser",
        }
    }
)


listWord = on_command(cmd="违禁词列表", priority=10, block=False)
matcherManager.addMatcher("ban_word:listWord", listWord)
@listWord.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    msg: str = ""
    gid = str(event.group_id)
    await tools.init(gid)
    words = tools.get_word_list(gid)
    if not words:
        await listWord.finish("未设置违禁词")
    else:
        word_list_message = "以下是违禁词列表,侮辱性或其他敏感词汇已内置,无须再添加:\n"
        for word in words:
            msg += f"{word},"
        await listWord.send(word_list_message + msg[:-1] + add_target(60))


clearWord = on_command(cmd="违禁词清空", aliases={"清空违禁词"}, priority=9, block=False)
@clearWord.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    tools.clear_words(str(event.group_id))
    await clearWord.send("已清空")
matcherManager.addMatcher("ban_word:clearWord", clearWord)


addWord = on_command(cmd="违禁词+", aliases={"添加违禁词", "违禁词添加"}, priority=8, block=False)
@addWord.handle()
async def _(event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
    gid = str(event.group_id)
    words = args.extract_plain_text().strip()
    if not words:
        await addWord.finish("违禁词呢?")
    words = tools.removeDuplicate(words.split("|"))
    exists_words = tools.wordsExist(gid, words)
    if exists_words:
        msg = "以下关键词添加失败:\n"
        having_pre = exists_words.get("having_pre")
        having_preEasy = exists_words.get("having_preEasy")
        having_custom = exists_words.get("having_custom")
        if having_pre:
            words = (words & having_pre) ^ words
            msg += f"\t以下关键字已存在于内置严格词典\n\t{','.join(having_pre).strip(',')}\n"
        if having_preEasy:
            words = (words & having_preEasy) ^ words
            msg += f"\t以下关键字已存在于内置简单词典\n\t{','.join(having_preEasy).strip(',')}\n"
        if having_custom:
            words = (words & having_custom) ^ words
            msg += f"\t以下关键字已存在于自定义词典\n\t{','.join(having_custom).strip(',')}\n"
    else:
        msg = "设置成功"
    tools.add_words(gid, words)
    await addWord.send(msg.strip("\n"))
matcherManager.addMatcher("ban_word:addWord", addWord)


addWordForce = on_command(cmd="违禁词++", aliases={"强制添加违禁词", "违禁词强制添加"}, priority=8, block=False)
@addWordForce.handle()
async def _(event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
    gid = str(event.group_id)
    words = args.extract_plain_text().strip()
    if not words:
        await addWordForce.finish("违禁词呢?")
    words = tools.removeDuplicate(words.split("|"))
    exists_words = tools.wordsExist(gid, words)
    msg = "设置成功"
    if exists_words:
        having_custom = exists_words.get("having_custom")
        if having_custom:
            words = (words & having_custom) ^ words
            msg = "以下关键词添加失败:\n"
            msg += f"\t以下关键字已存在于自定义词典\n\t{','.join(having_custom).strip(',')}\n"
    tools.add_words(gid, words)
    await addWordForce.send(msg.strip("\n"))
matcherManager.addMatcher("ban_word:addWordForce", addWordForce)


removeWord = on_command(cmd="违禁词-", aliases={"删除违禁词", "违禁词删除"}, priority=8, block=False)
@removeWord.handle()
async def _(event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
    gid = str(event.group_id)
    words = args.extract_plain_text().strip()
    if not words:
        await addWordForce.finish("违禁词呢?")
    words = tools.removeDuplicate(words.split("|"))
    tools.remove_words(gid, words)
    await removeWord.send("删除成功!")
matcherManager.addMatcher("ban_word:removeWord", removeWord)


easyLevel = on_command(cmd="简单违禁词", priority=8, block=False)
@easyLevel.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    tools.set_level(str(event.group_id), "easy")
    await easyLevel.send("设置成功")
matcherManager.addMatcher("ban_word:easyLevel", easyLevel)


strictLevel = on_command(cmd="严格违禁词", priority=8, block=False)
@strictLevel.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    tools.set_level(str(event.group_id), "strict")
    await strictLevel.send("设置成功")
matcherManager.addMatcher("ban_word:strictLevel", strictLevel)


noneLevel = on_command(cmd="关闭内置违禁词", aliases={"取消内置违禁词", "禁用内置违禁词"}, priority=8, block=False)
@noneLevel.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    tools.set_level(str(event.group_id), "none")
    await noneLevel.send("设置成功")
matcherManager.addMatcher("ban_word:noneLevel", noneLevel)

@event_preprocessor
async def _(event: GroupMessageEvent, bot: Bot):
    gid = str(event.group_id)
    if "启用" in event.get_plaintext() or "停用" in event.get_plaintext():
        return
    if "初始化" in event.get_plaintext():
        return
    if not (await get_state("ban_word", gid)):
        return
    # 不识别命令
    for pre in pres:
        if pre == event.get_message().extract_plain_text()[:len(pre)]:
            return
    await tools.init(gid)
    # 初始化设置
    uid = str(event.get_user_id())
    msg = event.get_message().extract_plain_text()
    message_id = event.message_id
    role: str = users.get_role(gid, uid)
    customWords: set = tools.get_word_list(gid)
    preBanWords: set = tools.get_word_pre()
    preBanWords_easy: set = tools.get_word_preEasy()
    level = tools.get_level(gid)
    # 检测是否触发关键词(自定义违禁词)
    for word in customWords:
        if word and word in msg:
            if not permission_(role, "superuser"):
                await tools.ban_count(uid, gid)
                count = users.get_ban_count(uid, gid)
                if count == 1:
                    times = "30min"
                elif count == 2:
                    times = "0.5day"
                else:
                    times = "1day"
                # 第n次踢出并拉黑
                if count >= ban_count_allow:
                    try:
                        await bot.delete_msg(message_id=message_id)
                        await tools.kick_user(uid, gid, bot)
                    except:
                        await bot.send(event=event, message="检测到违禁词,可能无管理员权限,无法进行处罚")
                        logger.info("触发违禁词:" + word)
                        raise IgnoredException("触发违禁词")
                    await bot.send(event=event, message=f"检测到违禁词,次数已达{ban_count_allow}次,踢出并拉黑")
                    logger.info("触发违禁词:" + word)
                    raise IgnoredException("触发违禁词")
                else:
                    try:
                        await bot.delete_msg(message_id=message_id)
                        await tools.ban_user(uid, gid, bot)
                    except:
                        await bot.send(event=event, message="检测到违禁词,可能无管理员权限,无法进行处罚")
                        logger.info("触发违禁词:" + word)
                        raise IgnoredException("触发违禁词")
                    await bot.send(event=event, message=f"检测到违禁词,第{count}次违规,禁言{times},请注意自己的言行",
                                   at_sender=True)
                    raise IgnoredException("触发违禁词")
            # 管理员不做限制
            else:
                logger.info(f"超级用户及以上({uid})触发自定义违禁词:" + word)
                break
    # 违禁词检测(内置违禁词)
    if level == "strict":
        for word in preBanWords:
            if word and word in msg:
                if role in ["member", "baned"]:
                    await bot.delete_msg(message_id=message_id)
                    await bot.call_api("set_group_ban", group_id=int(gid), user_id=int(uid), duration=300)
                    await bot.send(event=event, message=f"检测到违禁词,禁言5min,请注意自己的言行", at_sender=True)
                    logger.info("触发违禁词:" + word)
                    raise IgnoredException("触发违禁词")
                else:
                    logger.info(f"超级用户及以上({uid})触发内置严格违禁词:" + word)
                    break

    elif level == "easy":
        for word in preBanWords_easy:
            if word and word in msg:
                if role in ["member", "baned"]:
                    await bot.delete_msg(message_id=message_id)
                    await bot.call_api("set_group_ban", group_id=int(gid), user_id=int(uid), duration=300)
                    await bot.send(event=event, message=f"检测到违禁词,禁言5min,请注意自己的言行", at_sender=True)
                    logger.info("触发违禁词:" + word)
                    raise IgnoredException("触发违禁词")
                else:
                    logger.info(f"超级用户及以上({uid})触发内置简单违禁词:" + word)
                    break
