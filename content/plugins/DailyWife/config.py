"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/2 11:35
"""
import ujson as json

from nonebot import get_driver
from utils.json_tools import json_load, json_write
from utils.other import mk
from utils.path import DailyWife_path

botId = str(get_driver().config.bot_id)


class Config(object):
    gid: str
    scum: bool
    NTR: bool
    same_gender: bool
    bot: bool
    Self: bool
    activity: bool
    activity_time: int
    botId: str

    def __init__(self, gid: str):
        self.gid = gid
        self.botId = botId

    async def init(self):
        config_path = DailyWife_path / self.gid / "config.json"
        if not (DailyWife_path / self.gid).exists():
            (DailyWife_path / self.gid).mkdir(exist_ok=True, parents=True)
        if not config_path.exists():
            await mk("file", config_path, "w+", content=json.dumps(
                {"scum": True, "NTR": True, "same_gender": True, "bot": True, "Self": True, "activity": True, "activity_time": 31}))

        js = json_load(DailyWife_path / self.gid / "config.json")
        self.scum = js['scum']
        self.NTR = js['NTR']
        self.same_gender = js['same_gender']
        self.bot = js['bot']
        self.Self = js['Self']
        self.activity = js['activity']
        self.activity_time = js['activity_time']

    async def set_scum(self, scum: bool):
        self.scum = scum
        await self.save()

    async def set_NTR(self, NTR: bool):
        self.NTR = NTR
        await self.save()

    async def set_same_gender(self, same_gender: bool):
        self.same_gender = same_gender
        await self.save()

    async def set_bot(self, bot: bool):
        self.bot = bot
        await self.save()

    async def set_Self(self, Self: bool):
        self.Self = Self
        await self.save()

    async def set_activity(self, activity: bool):
        self.activity = activity
        await self.save()

    async def set_activity_time(self, activity_time: int):
        self.activity_time = activity_time
        await self.save()

    async def save(self):
        js = {"scum": self.scum, "NTR": self.NTR, "same_gender": self.same_gender, "bot": self.bot, "Self": self.Self, "activity": self.activity, "activity_time": self.activity_time}
        json_write(DailyWife_path / self.gid / "config.json", js)
