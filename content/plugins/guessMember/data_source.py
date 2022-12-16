"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/12/8 22:06
"""
import datetime
import random

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageSegment
from typing import Dict
from .game import Game
from .config import Config
from content.plugins.credit.tools import check, add, minus, get


class guessMember(object):
    gameList: Dict[str, Game]

    def __init__(self):
        self.gameList = {}

    def get_game(self, gid):
        return self.gameList[gid]

    def gameExist(self, gid: str):
        """
        游戏是否存在
        :param gid 群号
        """
        if gid in self.gameList and self.gameList[gid].active:
            return True
        return False

    def gameStart(self, gid: str, uid: str, bot, target_data: dict):
        """
        开始一个新游戏
        :param gid 群号
        :param uid 发起者QQ
        :param bot 机器人对象
        :param target_data 目标详细信息
        """
        minus(gid, uid, self.get_cost(gid))
        self.gameList.update({gid: Game(gid, uid, bot, target_data)})

    def gameOver(self, gid: str):
        """
        游戏结束
        :param gid 群号
        """
        try:
            self.gameList.pop(gid)
        except KeyError:
            pass

    def gameStop(self, gid: str):
        """
        手动结束游戏
        :param gid 群号
        """
        self.gameOver(gid)
        return f"游戏终止,总共用了 {self.gameList[gid].count} 次"

    def guessError(self, gid: str):
        if len(self.gameList[gid].clues) != 0:
            return [MessageSegment.text("猜错啦!再给你一个提示:")] + self.get_clue(gid)
        else:
            return self.Defeat(gid)

    def Win(self, gid: str):
        gameConfig = Config(gid)
        uid = self.gameList[gid].uid
        add(gid, uid, gameConfig.bonus)
        count = self.gameList[gid].count
        self.gameOver(gid)
        return f"回答正确!总共用了 {count} 次,增加 {gameConfig.bonus} 点积分"

    def Defeat(self, gid: str):
        self.gameOver(gid)
        return [MessageSegment.text("你输了!给了这么多的线索都猜不中!!!")]

    def is_target(self, gid: str, target_id: str):
        return self.gameList[gid].is_target(target_id)

    def is_active(self, gid: str):
        return self.gameList[gid].is_active()

    def get_clue(self, gid: str):
        """
        获得提示
        :param gid 群号
        """
        return self.gameList[gid].get_clue()

    def operator_check(self, gid, uid):
        if self.gameList[gid].uid != uid:
            return False
        return True

    def get_cost(self, gid: str):
        gameConfig = Config(gid)
        return gameConfig.cost

    def get_bouns(self, gid: str):
        gameConfig = Config(gid)
        return gameConfig.bonus

    def remove_member(self, uid: str, member_list: list):
        for member in member_list:
            if str(member['user_id']) == uid:
                member_list.remove(member)
                break

    def remove_inactive(self, gid: str, member_list: list):
        gameConfig = Config(gid)
        temp = member_list.copy()
        for member in temp:
            last_sent_time = datetime.datetime.fromtimestamp(member['last_sent_time'])
            if datetime.datetime.now() - last_sent_time > gameConfig.active_time:
                member_list.remove(member)

    def choice_target(self, uid: str, gid: str, member_list: list):
        gameConfig = Config(gid)
        if not gameConfig.bot_enable:
            bot_id = get_bot().self_id
            self.remove_member(bot_id, member_list)
        if not gameConfig.self_enable:
            self.remove_member(uid, member_list)
        if gameConfig.only_active:
            self.remove_inactive(gid, member_list)
        if not member_list:
            return None
        else:
            return random.choice(member_list)

    def credit_check(self, gid: str, uid: str):
        cost = self.get_cost(gid)
        if check(gid, uid, cost):
            return ""
        else:
            return f"积分不足,需要 {cost} 点积分,你还差 {cost - int(get(gid, uid))} 点积分"


