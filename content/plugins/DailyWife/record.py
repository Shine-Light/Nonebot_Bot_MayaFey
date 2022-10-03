"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/2 14:02
"""
import datetime
import json

from utils.json_tools import json_write, json_load
from utils.path import DailyWife_path
from utils.other import mk


class Record(object):
    gid: str
    record_path = None

    def __init__(self, gid: str):
        self.gid = gid

    async def init(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        record_path = DailyWife_path / self.gid / "record"
        daily_record_path = record_path / f"{today}.json"

        if not record_path.exists():
            record_path.mkdir(exist_ok=True, parents=True)
        if not daily_record_path.exists():
            await mk("file", daily_record_path, "w+", content=json.dumps({}))

        self.record_path = daily_record_path

    async def newWife(self, operator: dict, wife: dict):
        js = json_load(self.record_path)
        js.update({operator['user_id']: wife['user_id']})
        json_write(self.record_path, js)

    async def deleteWife(self, wife: dict):
        js = json_load(self.record_path)
        for user in js.keys():
            if js[user] == wife['user_id']:
                js.pop(user)
        json_write(self.record_path, js)

    async def deleteUser(self, user: dict):
        js = json_load(self.record_path)
        js.pop(user['user_id'])
        json_write(self.record_path, js)

    async def get_selected_list(self):
        return json_load(self.record_path)

    async def get_wife_id(self, operator: dict):
        return (await self.get_selected_list())[operator['user_id']]
