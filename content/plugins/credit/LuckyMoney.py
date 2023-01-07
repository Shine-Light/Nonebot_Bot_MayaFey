"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/1/6 16:38
"""
import random
import base64
import datetime

from pathlib import Path
from nonebot import require
from .tools import add
from utils.other import get_avatar
require("nonebot_plugin_htmlrender")
import nonebot_plugin_htmlrender as htmlrender


class LuckyMoneyManager(object):
    data: dict = {}

    def exist(self, gid: str):
        return gid in self.data

    def sendMoney(self, gid: str, uid: str, nickname: str, money: int, count: int):
        """
        发红包
        gid: 群号
        uid: 发起者QQ
        nickname: 发起者昵称
        money: 发出积分数
        count: 发出份数
        """
        self.data[gid] = {
            "uid": uid,
            "nickname": nickname,
            "money": money,
            "count": count,
            "money_surplus": money,
            "count_surplus": count,
            "record": []
        }
        clips = []
        for i in range(1, count + 1):
            r = random.randint(1, money - count + i)
            if i == count:
                r = money
            money -= r
            clips.append(r)
        self.data[gid].update({"clips": clips})

    def get_count(self, gid: str) -> int:
        """
        获取红包份数
        gid: 群号
        """
        return self.data.get(gid).get("count")

    def get_money_surplus(self, gid: str) -> int:
        """
        获取剩余积分
        gid: 群号
        """
        return self.data.get(gid).get("money_surplus")

    def get_count_surplus(self, gid: str) -> int:
        """
        获取剩余份数
        gid: 群号
        """
        return self.data.get(gid).get("count_surplus")

    def get_clips(self, gid: str) -> list:
        """
        获取积分分段
        gid: 群号
        """
        return self.data.get(gid).get("clips")

    def get_record(self, gid: str) -> list:
        """
        获取记录
        gid: 群号
        """
        return self.data.get(gid).get("record")

    def record(self, gid: str, uid: str, money: int, nickname: str):
        """
        记录信息
        gid: 群号
        uid: 操作者QQ
        money: 抢到的积分数
        nickname: 操作者昵称
        """
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        self.get_record(gid).append([uid, money, time_now, nickname])

    def sort(self, gid: str) -> list:
        """
        对记录信息按积分数进行降序排序
        gid: 群号
        """
        record = self.get_record(gid)
        record = sorted(record, key=(lambda x: x[1]), reverse=True)
        return record

    def fortunate(self, gid: str) -> str:
        """
        获取手气王QQ
        gid: 群号
        """
        record = self.sort(gid)
        return record[0]

    def remove_clips(self, gid: str, value: int):
        self.get_clips(gid).remove(value)

    def getMoney(self, gid: str, uid: str, nickname: str):
        """
        抢红包,返回抢到的积分数
        gid: 群号
        uid: 操作者QQ
        nickname: 操作者昵称
        """
        money = random.choice(self.get_clips(gid))
        self.remove_clips(gid, money)
        self.data.get(gid).update({"money_surplus": self.get_money_surplus(gid) - money})
        self.data.get(gid).update({"count_surplus": self.get_count_surplus(gid) - 1})
        self.record(gid, uid, money, nickname)
        add(gid, uid, money)
        return money

    def is_got(self, gid: str, uid: str):
        """
        用户是否已抢过红包
        """
        records = self.get_record(gid)
        for record in records:
            if record[0] == uid:
                return True
        return False

    def removeMoney(self, gid: str):
        """
        红包销毁
        gid: 群号
        """
        self.data.pop(gid)

    def backMoney(self, gid: str):
        """
        返还剩余积分
        gid: 群号
        """
        add(gid, self.data.get(gid).get("uid"), self.get_money_surplus(gid))

    async def generateSendImg(self, gid: str):
        """
        生成红包封面
        gid: 群号
        """
        sender_uid = self.data.get(gid).get('uid')
        sender_nickname = self.data.get(gid).get('nickname')
        sender_avatar = base64.b64encode(get_avatar(sender_uid))
        a = sender_avatar.decode()
        data = {
            "nickname": sender_nickname,
            "img_base64": sender_avatar.decode()
        }

        img = await htmlrender.template_to_pic(
            str(Path(__file__).parent / "template"),
            "index.html",
            data
        )
        return img

    async def generateEndImg(self, gid: str):
        """
        生成结算界面
        gid: 群号
        """
        records: list = self.sort(gid)[:5]
        money = self.data.get(gid).get('money')
        count = self.get_count(gid)
        sender_nickname = self.data.get(gid).get('nickname')
        sender_avatar = base64.b64encode(get_avatar(self.data.get(gid).get('uid'))).decode()
        data = {
            "money": money,
            "count": count,
            "sender_nickname": sender_nickname,
            "sender_avatar": sender_avatar
        }
        datas = []
        for record in records:
            avatar = base64.b64encode(get_avatar(record[0])).decode()
            datas.append({
                "avatar": avatar,
                "record": record,
                "achievement": ""
            })
        datas[0].update({"achievement": "手气最佳"})
        data.update({"datas": datas})

        img = await htmlrender.template_to_pic(
            str(Path(__file__).parent / "template"),
            "index2.html",
            {"data": data}
        )

        return img
