"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 19:56
"""
import asyncio
import base64
import ujson as json
import random
import re

import aiofiles
import nonebot

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ims.v20201229 import ims_client, models
from typing import Union, Optional
from nonebot import logger, get_driver, get_bot
from nonebot.adapters.onebot.v11 import Message, Bot

su = nonebot.get_driver().config.superusers
TencentID = nonebot.get_driver().config.tenid
TencentKeys = nonebot.get_driver().config.tenkeys
config = get_driver().config


async def replace_tmr(msg: str) -> str:
    """
    原始消息简单处理
    :param msg: 消息字符串
    :return: 去除cq码,链接等
    """
    find_cq = re.compile(r"(\[CQ:.*])")
    find_link = re.compile("(https?://.*[^\u4e00-\u9fa5])")
    cq_code = re.findall(find_cq, msg)
    for cq in cq_code:
        msg = msg.replace(cq, "")
    links = re.findall(find_link, msg)
    for link in links:
        msg = msg.replace(link, "链接")
    return msg


async def participle_simple_handle() -> set:
    """
    wordcloud停用词
    """
    prep_ = ['么', '了', '与', '不', '且', '之', '为', '兮', '其', '到', '云', '阿', '却', '个',
             '以', '们', '价', '似', '讫', '诸', '取', '若', '得', '逝', '将', '夫', '头', '只',
             '吗', '向', '吧', '呗', '呃', '呀', '员', '呵', '呢', '哇', '咦', '哟', '哉', '啊',
             '哩', '啵', '唻', '啰', '唯', '嘛', '噬', '嚜', '家', '如', '掉', '给', '维', '圪',
             '在', '尔', '惟', '子', '赊', '焉', '然', '旃', '所', '见', '斯', '者', '来', '欤',
             '是', '毋', '曰', '的', '每', '看', '着', '矣', '罢', '而', '耶', '粤', '聿', '等',
             '言', '越', '馨', '趴', '从', '自从', '自', '打', '到', '往', '在', '由', '向', '于',
             '至', '趁', '当', '当着', '沿着', '顺着', '按', '按照', '遵照', '依照', '靠', '本着',
             '用', '通过', '根据', '据', '拿', '比', '因', '因为', '由于', '为', '为了', '为着',
             '被', '给', '让', '叫', '归', '由', '把', '将', '管', '对', '对于', '关于', '跟', '和', '给', '替', '向', '同', '除了']

    pron_ = ["各个", "本人", "这个", "各自", "哪些", "怎的", "我", "大家", "她们", "多少", "怎么", "那么", "那样", "怎样", "几时", "哪儿", "我们", "自我",
             "什么", "哪个", "那个", "另外", "自己", "哪样", "这儿", "那些", "这样", "那儿", "它们", "它", "他", "你", "谁", "今", "吗", "是", "乌",
             "如何", "彼此", "其次", "列位", "该", "各", "然", "安", "之", "怎", "夫", "其", "每", "您", "伊", "此", "者", "咱们", "某", "诸位",
             "这些", "予", "任何", "若", "彼", "恁", "焉", "兹", "俺", "汝", "几许", "多咱", "谁谁", "有些", "干吗", "何如", "怎么样", "好多", "哪门子",
             "这程子", "他人", "奈何", "人家", "若干", "本身", "旁人", "其他", "其余", "一切", "如此", "谁人", "怎么着", "那会儿", "自家", "哪会儿", "谁边",
             "这会儿", "几儿", "这么些", "那阵儿", "那么点儿", "这么点儿", "这么样", "这阵儿", "一应", "多会儿", "何许", "若何", "大伙儿", "几多", "恁地", "谁个",
             "乃尔", "那程子", "多早晚", "如许", "倷", "孰", "侬", "怹", "朕", "他们", "这么着", "那么些", "咱家", "你们", "那么着"]

    others_ = ['就', '这', '那', '都', '也', '还', '又', '有', '没', '好', '我', '我的', '说', '去', '点', '不是', '就是', '要', '一个', '现在',
               '啥']

    sum_ = set(prep_ + pron_ + others_)
    return sum_


async def banSb(gid: Union[str, int], ban_list: list, time: int = None):
    """
    构造禁言
    :param gid: 群号
    :param ban_list: qq列表
    :param time: 时间（s),不填则随机
    :return:禁言操作
    """
    if time is None:
        time = random.randint(int(config.ban_rand_time_min), int(config.ban_rand_time_max))

    for qq in ban_list:
        bot: Bot = get_bot()
        await bot.set_group_ban(group_id=int(gid), user_id=int(qq), duration=time)


async def banWholeGroup(gid: Union[str, int], enable: bool = True):
    """
    全员禁言/解禁
    gid: 群号
    enable: 是否禁言,默认 True
    """
    bot: Bot = get_bot()
    await bot.set_group_whole_ban(group_id=int(gid), enable=enable)


async def image_moderation_async(img: Union[str, bytes]) -> dict:
    try:
        resp = await asyncio.to_thread(image_moderation, img)
        if resp["Suggestion"] == "Block":
            return {"status": False, "message": resp["Label"]}
        else:
            return {"status": True, "message": None}
    except Exception as e:
        return {"status": "error", "message": e}


# TENCENT 图片检测 @A60 https://github.com/djkcyl/ABot-Graia
def image_moderation(img):
    try:
        cred = credential.Credential(
            TencentID,
            TencentKeys,
        )
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ims.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ims_client.ImsClient(cred, "ap-shanghai", clientProfile)

        req = models.ImageModerationRequest()
        params = (
            {"BizType": "group_recall", "FileUrl": img}
            if type(img) == str
            else {"BizType": "group_recall", "FileContent": bytes_to_base64(img)}
        )
        req.from_json_string(json.dumps(params))

        resp = client.ImageModeration(req)
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        return err
    except KeyError as kerr:
        return kerr


def bytes_to_base64(data):
    return base64.b64encode(data).decode("utf-8")


def At(data: Union[str, dict, Message]):
    """
    检测at了谁，返回[qq, qq, qq,...]
    包含全体成员直接返回['all']
    如果没有at任何人，返回[]
    :param data: event.json
    :return: list
    """
    try:
        qq_list = []
        if isinstance(data, Message):
            for msg in data:
                if msg.type == "at":
                    if 'all' not in str(msg):
                        qq_list.append(int(msg.get("data")["qq"]))
                    else:
                        return ['all']
        elif isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, dict):
            for msg in data["original_message"]:
                if msg["type"] == "at":
                    if 'all' not in str(msg):
                        qq_list.append(int(msg.get("data")["qq"]))
                    else:
                        return ['all']
        return qq_list
    except KeyError:
        return []
