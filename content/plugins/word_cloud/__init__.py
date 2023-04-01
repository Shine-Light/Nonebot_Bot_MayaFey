"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 19:55
"""
import random
import os
import time
import httpx

from imageio import imread
from nonebot import on_command, logger, on_message, require, get_bot
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.internal.adapter import Message
from nonebot.exception import ActionFailed
from nonebot.plugin import PluginMetadata
from utils.admin_tools import replace_tmr, participle_simple_handle
from utils.path import *
from . import tools
from utils import requests_tools
from utils.matcherManager import matcherManager
from utils.other import add_target
from content.plugins.plugin_control.functions import get_state


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="word_cloud",
    description="群词云",
    usage="/群词云\n"
          "/记录本群 (超级用户)\n"
          "/停止记录本群 (超级用户)\n"
          "/更新mask (超级用户)" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "baned",
        "permission_special": {
            "word_cloud:word_start": "superuser",
            "word_cloud:word_stop": "superuser",
            "word_cloud:cloud": "member",
            "word_cloud:update_mask": "superuser",
        },
        "unset": False,
        "total_unable": True,
        "author": "yzyyz1387",
        "translate": "群词云",
    }
)


words = limit_word_path
words_easy = limit_word_path_easy
fts: str = "%Y-%m-%d"
ft: str = "%Y-%m-%d %H:%M:%S"


word_start = on_command("记录本群", block=False, priority=4)
matcherManager.addMatcher("word_cloud:word_start", word_start)
@word_start.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    await tools.init()
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


word_stop = on_command("停止记录本群", block=False, priority=4)
matcherManager.addMatcher("word_cloud:word_stop", word_stop)
@word_stop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    await tools.init()
    txt = open(word_path, 'r', encoding='utf-8').read()
    if gid in txt:
        with open(word_path, 'w', encoding='utf-8') as c:
            c.write(txt.replace(gid, ""))
            c.close()
            logger.info(f"停止记录{gid}")
            await word_stop.finish("成功，曾经的记录不会被删除")
    else:
        logger.info(f"停用失败：{gid}不存在")
        await word_stop.finish(f"停用失败：{gid}不存在")


word = on_message(priority=12, block=False)
@word.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    记录聊天内容
    :param bot:
    :param event:
    :return:
    """
    await tools.init()
    date: str = time.strftime(fts, time.localtime())

    if not os.path.exists(re_wordcloud_img_path / date):
        os.mkdir(re_wordcloud_img_path / date)
    if not os.path.exists(words_contents_path / date):
        os.mkdir(words_contents_path / date)
    # QQ管家不记录
    if str(event.user_id) == "2854196310":
        await word.finish()
    # 违禁词不记录
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
matcherManager.addMatcher("word_cloud:cloud", cloud)
@cloud.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    from wordcloud import WordCloud, ImageColorGenerator
    import jieba
    txt = open(word_path, "r", encoding="utf-8").read().split("\n")
    if gid not in txt:
        await cloud.finish("该群未开启词云")
    date: str = time.strftime(fts, time.localtime())
    if not os.path.exists(re_wordcloud_img_path / date):
        os.mkdir(re_wordcloud_img_path / date)
    if not os.path.exists(words_contents_path / date):
        os.mkdir(words_contents_path / date)
    localTime = time.strftime(ft, time.localtime())

    background_img = os.listdir(wordcloud_bg_path)
    if background_img:
        wordcloud_bg = random.choice(os.listdir(wordcloud_bg_path))
        try:
            async with httpx.AsyncClient() as client:
                num = int((await client.get(
                    "https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/num.txt")).read())
                if num > len(background_img):
                    await cloud.send(f"开发者新提供了{num - len(background_img)}张图片，您可以发送【更新mask】下载新的图片")
        except:
            pass
    else:
        try:
            async with httpx.AsyncClient() as client:
                range_ = int((await client.get("https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/num.txt")).read())
                logger.info(f"获取到{range_}张mask图片")
                for i in range(range_):
                    wordcloud_bg = await client.get(await requests_tools.match_30X(f"https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/bg{i}.png"))
                    logger.info(f"正下载{i}张mask图片")
                    with open(wordcloud_bg_path / f"{i}.png", "wb") as f:
                        f.write(wordcloud_bg.content)
        except Exception as e:
            logger.error("下载词云mask图片出现错误")
            return
        wordcloud_bg = random.choice(os.listdir(wordcloud_bg_path))
    background_image = imread(wordcloud_bg_path / wordcloud_bg)
    ttf_name_ = Path() / "resource" / "font" / "msyhblod.ttf"
    path_temp = words_contents_path / date / f"{str(gid)}.txt"
    dir_list = os.listdir(words_contents_path / date)
    if gid + ".txt" in dir_list:
        text = open(path_temp).read()
        txt = jieba.lcut(text)
        stop_ = await participle_simple_handle()
        string = " ".join(txt)
        try:
            # 关键词不为空
            if string != " ":
                wc = WordCloud(font_path=str(ttf_name_.resolve()),
                               width=1920, height=1080, mode='RGBA',
                               background_color="#ffffff",
                               mask=background_image,
                               stopwords=stop_).generate(string)
                img = Path(re_wordcloud_img_path / f"wordcloud_{gid}.png")
                img_colors = ImageColorGenerator(background_image, default_color=(255, 255, 255))
                wc.recolor(color_func=img_colors)
                wc.to_file(img)
                await cloud.send(Message([MessageSegment.text(f"当前时间:{localTime}")
                                         , MessageSegment.image(img)]))
        except ActionFailed:
            await cloud.send(message=f"API调用错误,可能是信息错误或账号风控,具体参考go-cqhttp输出")
        except ValueError:
            await cloud.send("无聊天记录,无法生成词云")
        except Exception as err:
            await cloud.send(f"出现错误{type(err)}:{err}")
    else:
        await cloud.send("无聊天记录,无法生成词云")


timezone = "Asia/Shanghai"
scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job("cron", hour="19", minute="0",second="0", timezone=timezone)
async def run():
    from wordcloud import WordCloud, ImageColorGenerator
    import jieba
    date: str = time.strftime(fts, time.localtime())
    if not os.path.exists(re_wordcloud_img_path / date):
        os.mkdir(re_wordcloud_img_path / date)
    if not os.path.exists(words_contents_path / date):
        os.mkdir(words_contents_path / date)

    file = open(word_path)
    bot = get_bot()

    for gid in file:
        gid = gid.strip("\n")
        if not gid:
            continue
        if await get_state("word_cloud", gid):
            localTime = time.strftime(ft, time.localtime())
            path_temp = words_contents_path / date / f"{str(gid)}.txt"
            if not os.path.exists(path_temp):
                continue
            background_img = os.listdir(wordcloud_bg_path)
            if background_img:
                wordcloud_bg = random.choice(os.listdir(wordcloud_bg_path))
                try:
                    async with httpx.AsyncClient() as client:
                        num = int((await client.get(
                            "https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/num.txt")).read())
                        if num > len(background_img):
                            await cloud.send(f"开发者新提供了{num - len(background_img)}张图片，您可以发送【更新mask】下载新的图片")
                except:
                    pass
            else:
                try:
                    async with httpx.AsyncClient() as client:
                        range_ = int((await client.get(
                            "https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/num.txt")).read())
                        logger.info(f"获取到{range_}张mask图片")
                        for i in range(range_):
                            wordcloud_bg = await client.get(await requests_tools.match_30X(
                                f"https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/bg{i}.png"))
                            logger.info(f"正下载{i}张mask图片")
                            with open(wordcloud_bg_path / f"{i}.png", "wb") as f:
                                f.write(wordcloud_bg.content)
                except Exception as e:
                    logger.error("下载词云mask图片出现错误")
                    return
                wordcloud_bg = random.choice(os.listdir(wordcloud_bg_path))
            background_image = imread(wordcloud_bg_path / wordcloud_bg)
            ttf_name_ = Path() / "resource" / "font" / "msyhblod.ttf"

            text = open(path_temp).read()
            txt = jieba.lcut(text)
            stop_ = await participle_simple_handle()
            string = " ".join(txt)
            try:
                # 关键词不为空
                if string:
                    wc = WordCloud(font_path=str(ttf_name_.resolve()),
                                   width=1920, height=1080, mode='RGBA',
                                   background_color="#ffffff",
                                   mask=background_image,
                                   stopwords=stop_).generate(string)
                    img = Path(re_wordcloud_img_path / f"wordcloud_{gid}.png")
                    img_colors = ImageColorGenerator(background_image, default_color=(255, 255, 255))
                    wc.recolor(color_func=img_colors)
                    wc.to_file(img)
                    await bot.send_group_msg(group_id=gid, message=Message([MessageSegment.text(f"当前时间:{localTime}")
                                             , MessageSegment.image(img)]))
            except ActionFailed:
                await bot.send_group_msg(group_id=gid, message=f"API调用错误,可能是信息错误或账号风控,具体参考go-cqhttp输出")
            except ValueError:
                logger.error("词云生成失败,可能聊天记录中无文本")
            except Exception as err:
                logger.error(f"{str(err)}")

    file.close()


update_mask = on_command("更新mask", aliases={'下载mask'}, block=False, priority=7)
matcherManager.addMatcher("word_cloud:update_mask", update_mask)
@update_mask.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    更新mask
    """
    already_have = len(os.listdir(wordcloud_bg_path))
    try:
        async with httpx.AsyncClient() as client:
            num_in_cloud = int((await client.get(
                "https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/num.txt")).read())
            if num_in_cloud > already_have:
                await update_mask.send("正zhai更新中...")
                for i in range(already_have, num_in_cloud):
                    img_content = (await client.get(
                        f"https://fastly.jsdelivr.net/gh/yzyyz1387/blogimages/nonebot/wordcloud/bg{i}.png")).content
                    with open(wordcloud_bg_path / f"{i}.png", "wb") as f:
                        f.write(img_content)
                await update_mask.send("更新完成（好耶）")
            elif num_in_cloud == already_have:
                await update_mask.send("蚌！已经是最新了耶")
    except Exception as e:
        logger.info(e)
        await update_mask.send(f"QAQ,更新mask失败:\n{e}")
        return
