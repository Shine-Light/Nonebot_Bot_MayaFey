"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 19:55
"""
from nonebot import on_command, logger, on_message, require, get_bot
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.internal.adapter import Message
from nonebot.exception import ActionFailed
from ..utils.admin_tools import replace_tmr, participle_simple_handle
import os
import time
from ..utils.path import *
from . import tools
from .. import permission, plugin_control
from ..utils import users


words = limit_word_path
words_easy = limit_word_path_easy
fts: str = "%Y-%m-%d"
ft: str = "%Y-%m-%d %H:%M:%S"


word_start = on_command("记录本群", block=True, priority=4)
@word_start.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "word_start", gid):
        with open(word_path, 'r+', encoding='utf-8') as c:
            txt = c.read().split("\n")
            if gid not in txt:
                c.write(gid + "\n")
                c.close()
                logger.info(f"开始记录{gid}")
                await word_start.finish("成功")
            else:
                logger.info(f"{gid}已存在")
                await word_start.finish(f"{gid}已存在")
    else:
        await word_start.send("无权限")


word_stop = on_command("停止记录本群", block=True, priority=4)
@word_stop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "word_stop", gid):
        txt = open(word_path, 'r', encoding='utf-8').read()
        if gid in txt:
            with open(word_path, 'w', encoding='utf-8') as c:
                c.write(txt.replace(gid, ""))
                c.close()
                logger.info(f"停止记录{gid}")
                await word_start.finish("成功，曾经的记录不会被删除")
        else:
            logger.info(f"停用失败：{gid}不存在")
            await word_start.finish(f"停用失败：{gid}不存在")
    else:
        await word_stop.send("无权限")

word = on_message(priority=12)
@word.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    记录聊天内容
    :param bot:
    :param event:
    :return:
    """
    date: str = time.strftime(fts, time.localtime())
    if not os.path.exists(re_img_path / date):
        os.mkdir(re_img_path / date)
    if not os.path.exists(words_contents_path / date):
        os.mkdir(words_contents_path / date)
    if str(event.user_id) == "2854196310":
        await word.finish()
    for wd in open(words, "r", encoding="utf-8"):
        if wd in event.get_message():
            await word.finish()
    for wd in open(words_easy, "r", encoding="utf-8"):
        if wd in event.get_message():
            await word.finish()

    gid = str(event.group_id)
    msg = str(event.get_message()).replace(" ", "")
    path_temp = words_contents_path / date / f"{str(gid)}.txt"
    txt = open(word_path, "r", encoding="utf-8").read().split("\n")
    if gid in txt:
        msg = await replace_tmr(msg)
        with open(path_temp, "a+") as c:
            c.write(msg + "\n")


cloud = on_command("群词云", priority=5)
@cloud.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "cloud", gid):
        from wordcloud import WordCloud
        import jieba
        txt = open(word_path, "r", encoding="utf-8").read().split("\n")
        if gid not in txt:
            await cloud.finish("该群未开启词云")
        date: str = time.strftime(fts, time.localtime())
        if not os.path.exists(re_img_path / date):
            os.mkdir(re_img_path / date)
        if not os.path.exists(words_contents_path / date):
            os.mkdir(words_contents_path / date)
        localTime = time.strftime(ft, time.localtime())

        ttf_name_ = Path() / "resource" / "font" / "msyhblod.ttf"
        path_temp = words_contents_path / date / f"{str(gid)}.txt"
        dir_list = os.listdir(words_contents_path / date)
        if gid + ".txt" in dir_list:
            text = open(path_temp).read()
            txt = jieba.lcut(text)
            stop_ = await participle_simple_handle()
            string = " ".join(txt)
            try:
                wc = WordCloud(font_path=str(ttf_name_.resolve()), width=800, height=600, mode='RGBA',
                               background_color="#ffffff", stopwords=stop_).generate(string)
                img = Path(re_img_path / date / f"{gid}.png")
                wc.to_file(img)
                dir_path = os.path.dirname(os.path.abspath(__file__))
                dir_path = dir_path.replace(f"content{os.sep}plugins{os.sep}word_cloud", "")
                img = f"file:///{dir_path}{tools.format_path(img)}"
                message = Message([MessageSegment.text(f"当前时间:{localTime},今日群词云:"), MessageSegment.image(img)])
                await bot.send(message=message, event=event)
            except ActionFailed:
                await cloud.send(message=f"API调用错误,可能是信息错误或账号风控,具体参考go-cqhttp输出")
            except Exception as err:
                await cloud.send(f"出现错误{type(err)}:{err}")

    else:
        await cloud.send("无权限,权限需在 成员 及以上")


timezone = "Asia/Shanghai"
scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job("cron", hour="19", minute="00", timezone=timezone)
async def run():
    from wordcloud import WordCloud
    import jieba
    date: str = time.strftime(fts, time.localtime())
    if not os.path.exists(re_img_path / date):
        os.mkdir(re_img_path / date)
    if not os.path.exists(words_contents_path / date):
        os.mkdir(words_contents_path / date)

    localTime = time.strftime(ft, time.localtime())
    txt = open(word_path)
    bot = get_bot()

    for gid in txt:
        gid = gid.strip("\n")
        if not gid:
            break
        if await plugin_control.get_state("word_cloud", gid):
            path_temp = words_contents_path / date / f"{str(gid)}.txt"
            dir_list = os.listdir(words_contents_path / date)
            if gid + ".txt" in dir_list:
                text = open(path_temp).read()
                txt = jieba.lcut(text)
                stop_ = await participle_simple_handle()
                string = " ".join(txt)
                try:
                    wc = WordCloud(font_path=str(ttf_name.resolve()), width=800, height=600, mode='RGBA',
                                   background_color="#ffffff", stopwords=stop_).generate(string)
                    img = re_img_path / date / f"{gid}.png"
                    wc.to_file(img)
                    # await cloud.send(MessageSegment.image(img))
                    dir_path = os.path.dirname(os.path.abspath(__file__))
                    dir_path = dir_path.replace(f"content{os.sep}plugins{os.sep}word_cloud", "")
                    dir_path = dir_path.replace("\\", "/")
                    img = f"file:///{dir_path}{tools.format_path(img)}"
                    await bot.send_group_msg(
                        group_id=gid,
                        message=Message([MessageSegment.text(f"当前时间:{localTime},今日群词云:"), MessageSegment.image(img)])
                    )
                except ActionFailed:
                    await bot.send_group_msg(group_id=gid, message=f"API调用错误,可能是信息错误或账号风控,具体参考go-cqhttp输出")
                except Exception as err:
                    await bot.send_group_msg(group_id=gid, message=f"出现错误{type(err)}:{err}")
    txt.close()
