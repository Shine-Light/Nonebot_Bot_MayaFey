"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/2 11:35
"""
import random
import datetime

from .config import Config
from .record import Record


class DailyWife(object):
    gid: str
    operator: dict
    member_list: list
    config: Config
    record: Record

    def __init__(self, operator: dict, member_list: list):
        self.gid = str(operator['group_id'])
        self.operator = operator
        self.gender = operator['sex']
        self.member_list = member_list
        self.config = Config(self.gid)
        self.record = Record(self.gid)

    async def init(self):
        await self.config.init()
        await self.record.init()
        if not self.config.NTR:
            await self.remove_NTR()
        if self.config.activity:
            await self.remove_inactive()
        if not self.config.same_gender:
            await self.remove_same_gender()

    async def randomWife(self):
        wife = {}
        while len(self.member_list):
            wife = random.choice(self.member_list)
            wife['user_id'] = str(wife['user_id'])
            if not (self.config.bot and self.config.Self):
                if not self.config.bot:
                    if str(wife['user_id']) != self.config.botId:
                        pass
                    else:
                        self.member_list.remove(wife)
                        continue
                if not self.config.Self:
                    if str(wife['user_id']) != self.operator['user_id']:
                        break
                    else:
                        self.member_list.remove(wife)
                        continue
                else:
                    break
            else:
                break

        if len(self.member_list) == 0:
            wife = {}
        else:
            await self.record.newWife(self.operator, wife)

        return wife

    async def have_wife(self):
        selected_list = self.record.get_selected_list()
        if self.operator['user_id'] in selected_list:
            return True
        return False

    async def remove_inactive(self):
        today = datetime.datetime.now()
        copy = self.member_list[:]
        for member in copy:
            last_time = datetime.datetime.fromtimestamp(member['last_sent_time'])
            if today - last_time > datetime.timedelta(days=self.config.activity_time):
                self.member_list.remove(member)

    async def remove_same_gender(self):
        copy = self.member_list[:]
        for member in copy:
            if member['sex'] == self.gender:
                self.member_list.remove(member)

    async def remove_NTR(self):
        if not self.record.get_selected_list():
            return
        copy = self.member_list[:]
        for member in copy:
            selected_list = await self.record.get_selected_list()
            for selected in selected_list:
                if str(member['user_id']) == selected_list[selected]:
                    self.member_list.remove(member)
