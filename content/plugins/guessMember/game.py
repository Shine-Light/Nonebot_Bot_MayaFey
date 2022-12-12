"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/12/8 22:07
"""
import random

import requests
import datetime

from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message
from utils.users import get_role
from utils.path import guessMember_cache_path
from .config import Config
from .tools import mosaic, blur, cut

fmt_str = "%Y-%m-%d %H:%M:%S"


class Target(object):
    gid: str
    uid: str
    nickname: str
    card: str
    sex: str
    age: str
    area: str
    join_time: datetime.datetime
    last_sent_time: datetime.datetime
    level: int
    role: str
    title: str

    def __init__(self, data: dict):
        self.gid = str(data['group_id'])
        self.uid = str(data['user_id'])
        self.nickname = data['nickname']
        self.card = data['card']
        if data['sex'] == 'male':
            self.sex = '男'
        elif data['sex'] == 'female':
            self.sex = '女'
        else:
            self.sex = data['sex']
        self.age = data['age']
        self.area = data['area']
        self.join_time = datetime.datetime.fromtimestamp(data['join_time'])
        self.last_sent_time = datetime.datetime.fromtimestamp(data['last_sent_time'])
        self.level = int(data['level'])
        self.role = get_role(self.gid, self.uid)
        self.title = data['title']


class Game(object):
    gid: str
    uid: str
    target: Target
    last_active: datetime.datetime
    active: bool
    bot: Bot
    config: Config
    count: int
    clues: list

    def __init__(self, gid: str, uid: str, bot: Bot, target_data: dict):
        """
        :param gid 游戏群号
        :param uid 发起者QQ
        :param bot 机器人对象
        """
        self.gid = gid
        self.uid = uid
        self.last_active = datetime.datetime.now()
        self.active = True
        self.bot = bot
        self.target = Target(target_data)
        self.config = Config(gid)
        self.count = 0
        self.clues = [self.get_nickname, self.get_card, self.get_sex, self.get_age, self.get_area, self.get_join_time,
                      self.get_last_sent_time, self.get_level, self.get_role, self.get_title, self.get_blur_avatar,
                      self.get_mosaic_avatar, self.get_cut_avatar]

    def is_target(self, target_uid: str):
        self.count += 1
        self.last_active = datetime.datetime.now()
        if target_uid == self.target.uid:
            return True
        return False

    def is_active(self):
        """
        游戏是否过期
        """
        if datetime.datetime.now() - self.last_active > self.config.out_time:
            self.active = False
        return self.active

    def get_clue(self):
        """
        获得提示
        """
        try:
            if self.target.title == "":
                self.clues.remove(self.get_title)
            if self.target.sex == "unknown":
                self.clues.remove(self.get_sex)
            if self.target.area == "":
                self.clues.remove(self.get_area)
            if self.target.level == 1:
                self.clues.remove(self.get_level)
            if self.target.card == "":
                self.clues.remove(self.get_card)
        except ValueError:
            pass

        # clue = self.clues[0]  # 测试用
        clue = random.choice(self.clues)
        self.clues.remove(clue)

        return clue()

    def get_avatar(self):
        avatar = requests.get(f"http://q.qlogo.cn/headimg_dl?dst_uin={self.target.uid}&spec=640&img_type=jpg").content
        return avatar

    def blue_avatar(self):
        blur(self.get_avatar())
        return [MessageSegment.image(guessMember_cache_path)]

    def mosaic_avatar(self):
        mosaic(self.get_avatar())
        return [MessageSegment.image(guessMember_cache_path)]

    def cut_avatar(self):
        cut(self.get_avatar(), int(self.config.cut_length * 640))
        return [MessageSegment.image(guessMember_cache_path)]

    def get_nickname(self):
        return [MessageSegment.text(f"TA的昵称中含有 {self.target.nickname[random.randint(0, len(self.target.nickname) - 1)]}")]

    def get_card(self):
        return [MessageSegment.text(f"TA的群名片中含有 {self.target.card[random.randint(0, len(self.target.card) - 1)]}")]

    def get_sex(self):
        return [MessageSegment.text(f"TA的性别是 {self.target.sex}")]

    def get_age(self):
        return [MessageSegment.text(f"TA今年 {self.target.age} 岁了")]

    def get_area(self):
        return [MessageSegment.text(f"TA现在在 {self.target.area}")]

    def get_join_time(self):
        return [MessageSegment.text(f"TA是在 {self.target.join_time.strftime(fmt_str)} 加入的")]

    def get_last_sent_time(self):
        return [MessageSegment.text(f"TA最后一次发言是在 {self.target.last_sent_time.strftime(fmt_str)}")]

    def get_level(self):
        return [MessageSegment.text(f"TA的QQ等级是 {self.target.level}")]

    def get_role(self):
        return [MessageSegment.text(f"TA的权限是 {self.target.role}")]

    def get_title(self):
        return [MessageSegment.text(f"TA在本群的头衔是 {self.target.title}")]

    def get_blur_avatar(self):
        return [MessageSegment.text(f"TA的头像模糊后是这样的:")] + self.blue_avatar()

    def get_mosaic_avatar(self):
        return [MessageSegment.text(f"TA的头像打码后是这样的:")] + self.mosaic_avatar()

    def get_cut_avatar(self):
        return [MessageSegment.text(f"TA的头像有这样一部分:")] + self.cut_avatar()
