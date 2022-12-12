"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/12/9 12:58
"""
import datetime

from utils.json_tools import json_load, json_write
from utils.path import guessMember_path
from .tools import S2B, B2S


class Config(object):
    gid: str
    cost: int
    bonus: int
    out_time: datetime.timedelta
    self_enable: bool
    bot_enable: bool
    only_active: bool
    active_time: datetime.timedelta
    cut_length: float

    def __init__(self, gid: str):
        self.gid = gid
        data = json_load(guessMember_path / gid / "config.json")
        self.cost = data['cost']
        self.bonus = data['bonus']
        self.out_time = datetime.timedelta(seconds=data['out_time'])
        self.self_enable = data['self_enable']
        self.bot_enable = data['bot_enable']
        self.only_active = data['only_active']
        self.active_time = datetime.timedelta(days=data['active_time'])
        self.cut_length = float(data['cut_length'])

    def set_cost(self, cost: int):
        try:
            self.cost = int(cost)
        except:
            return "积分必须是整数!"
        self.save()

    def set_bonus(self, bonus: int):
        try:
            self.bonus = int(bonus)
        except:
            return "积分必须是整数!"
        self.save()

    def set_out_time(self, out_time: int):
        try:
            self.out_time = datetime.timedelta(seconds=int(out_time))
        except:
            return "秒数必须是整数!"
        self.save()

    def set_self_enable(self, self_enable: str):
        self_enable = S2B(self_enable)
        if type(self_enable) == bool:
            self.self_enable = self_enable
        else:
            return "开还是不开?"
        self.save()

    def set_bot_enable(self, bot_enable: str):
        bot_enable = S2B(bot_enable)
        if type(bot_enable) == bool:
            self.bot_enable = bot_enable
        else:
            return "开还是不开?"
        self.save()

    def set_only_active(self, only_active: str):
        only_active = S2B(only_active)
        if type(only_active) == bool:
            self.only_active = only_active
        else:
            return "开还是不开?"
        self.save()

    def set_active_time(self, out_time: int):
        try:
            self.active_time = datetime.timedelta(days=int(out_time))
        except:
            return "天数必须是整数!"
        self.save()

    def set_cut_length(self, cut_length: float):
        try:
            if cut_length > 1:
                return "百分比不能大于1!"
            self.cut_length = float(cut_length)
        except:
            return "百分比必须是整数或小数!"
        self.save()

    def save(self):
        data = {
            "out_time": self.out_time.seconds,
            "cost": self.cost,
            "bonus": self.bonus,
            "self_enable": self.self_enable,
            "bot_enable": self.bot_enable,
            "only_active": self.only_active,
            "active_time": self.active_time.days,
            "cut_length": self.cut_length
        }
        json_write(guessMember_path / self.gid / "config.json", data)

    def __str__(self):
        return f"当前群的猜群友配置:\n" \
                 f"超时时间: {self.out_time.seconds} 秒\n" \
                 f"消耗积分: {self.cost}\n" \
                 f"奖励积分: {self.bonus}\n" \
                 f"抽到机器人: {B2S(self.bot_enable)}\n" \
                 f"抽到自己: {B2S(self.self_enable)}\n" \
                 f"潜水成员不参与: {B2S(self.only_active)}\n" \
                 f"潜水时间阈值: {self.active_time.days} 天\n" \
                 f"头像切割大小百分比: {self.cut_length}"
