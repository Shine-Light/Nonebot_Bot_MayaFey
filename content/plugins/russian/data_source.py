from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment, Bot
from typing import Optional, Tuple, Union, List, Dict
from nonebot.log import logger
from pathlib import Path
import nonebot
import asyncio
import random
import time
import os
from .config import Config
from utils import database_mysql

try:
    import ujson as json
except ModuleNotFoundError:
    import json

cursor = database_mysql.cursor
database = database_mysql.connect

global_config = nonebot.get_driver().config
russian_config = Config.parse_obj(global_config.dict())

# 签到金币随机范围
sign_gold = russian_config.sign_gold
# bot昵称
bot_name = list(global_config.nickname)[0] if global_config.nickname else "本裁判"
# 最大赌注
max_bet_gold = russian_config.max_bet_gold
russian_path = russian_config.russian_path

russian_config = Config.parse_obj(nonebot.get_driver().config.dict())
max_bet_gold = russian_config.max_bet_gold


async def rank(player_data: dict, group_id: int, type_: str) -> str:
    """
    排行榜数据统计
    :param player_data: 玩家数据
    :param group_id: 群号
    :param type_: 排行榜类型
    """
    group_id = str(group_id)
    try:
        all_user = list(player_data[group_id].keys())
    except:
        return "该群未进行过游戏,无法显示排名"
    if type_ == "win_rank":
        rank_name = "胜场排行榜:\n"
        all_user_data = [player_data[group_id][x]["win_count"] for x in all_user]
    elif type_ == "lose_rank":
        rank_name = "败场排行榜:\n"
        all_user_data = [player_data[group_id][x]["lose_count"] for x in all_user]
    elif type_ == "make_gold":
        rank_name = "赢取金币排行榜:\n"
        all_user_data = [player_data[group_id][x]["make_gold"] for x in all_user]
    else:
        rank_name = "输掉金币排行榜:\n"
        all_user_data = [player_data[group_id][x]["lose_gold"] for x in all_user]
    rst = ""
    if all_user:
        for _ in range(len(all_user) if len(all_user) < 10 else 10):
            _max = max(all_user_data)
            _max_id = all_user[all_user_data.index(_max)]
            name = player_data[group_id][_max_id]["nickname"]
            rst += f"{name}：{_max}\n"
            all_user_data.remove(_max)
            all_user.remove(_max_id)
        rst = rst[:-1]
    return rank_name + rst


def random_bullet(num: int) -> List[int]:
    """
    随机子弹排列
    :param num: 装填子弹数量
    """
    bullet_lst = [0, 0, 0, 0, 0, 0, 0]
    for i in random.sample([0, 1, 2, 3, 4, 5, 6], num):
        bullet_lst[i] = 1
    return bullet_lst


class RussianManager:
    def __init__(self):
        self._player_data = {}
        self._current_player = {}
        file = russian_path / "russian_data.json"
        self.file = file
        file.parent.mkdir(exist_ok=True, parents=True)
        if not file.exists():
            old_file = Path(os.path.dirname(__file__)) / "russian_data.json"
            if old_file.exists():
                os.rename(old_file, file)
        if file.exists():
            with open(file, "r", encoding="utf8") as f:
                self._player_data = json.load(f)

    def accept(self, event: GroupMessageEvent) -> Union[str, Message]:
        """
        接受决斗请求
        :param event: event
        """
        self._init_player_data(event)
        try:
            if self._current_player[event.group_id][1] == 0:
                return "目前没有发起对决，你接受个啥？速速装弹！"
        except KeyError:
            return "目前没有进行的决斗，请发送 装弹 开启决斗吧！"
        if self._current_player[event.group_id][2] != 0:
            if (
                self._current_player[event.group_id][1] == event.user_id
                or self._current_player[event.group_id][2] == event.user_id
            ):
                return f"你已经身处决斗之中了啊，给我认真一点啊！"
            else:
                return "已经有人接受对决了，你还是乖乖等待下一场吧！"
        if self._current_player[event.group_id][1] == event.user_id:
            return "请不要自己枪毙自己！换人来接受对决..."
        if (
            self._current_player[event.group_id]["at"] != 0
            and self._current_player[event.group_id]["at"] != event.user_id
        ):
            return Message(
                f'这场对决是邀请 {MessageSegment.at(self._current_player[event.group_id]["at"])}的，不要捣乱！'
            )
        if time.time() - self._current_player[event.group_id]["time"] > 30:
            self._current_player[event.group_id] = {}
            return "这场对决邀请已经过时了，请重新发起决斗..."

        # user_money = self._player_data[str(event.group_id)][str(event.user_id)]["gold"]
        cursor.execute(f"SELECT credit FROM credit WHERE gid='{event.group_id}' AND uid='{event.user_id}'")
        user_money = cursor.fetchone()[0]
        if user_money < self._current_player[event.group_id]["money"]:
            if (
                self._current_player[event.group_id]["at"] != 0
                and self._current_player[event.group_id]["at"] == event.user_id
            ):
                self._current_player[event.group_id] = {}
                return "你的金币不足以接受这场对决！对决还未开始便结束了，请重新装弹！"
            else:
                return "你的金币不足以接受这场对决！"

        player2_name = event.sender.card if event.sender.card else event.sender.nickname

        self._current_player[event.group_id][2] = event.user_id
        self._current_player[event.group_id]["player2"] = player2_name
        self._current_player[event.group_id]["time"] = time.time()

        return Message(
            f"{player2_name}接受了对决！\n"
            f"请{MessageSegment.at(self._current_player[event.group_id][1])}先开枪！"
        )

    async def refuse(self, bot: Bot, event: GroupMessageEvent) -> Union[str, Message]:
        self._init_player_data(event)
        try:
            if self._current_player[event.group_id][1] == 0:
                return "你要拒绝啥？明明都没有人发起对决的说！"
        except KeyError:
            return "目前没有进行的决斗，请发送 装弹 开启决斗吧！"
        if (
            self._current_player[event.group_id]["at"] != 0
            and event.user_id != self._current_player[event.group_id]["at"]
        ):
            return "又不是找你决斗，你拒绝什么啊！气！"
        if self._current_player[event.group_id]["at"] == event.user_id:
            at_player_name = await bot.get_group_member_info(
                group_id=event.group_id, user_id=event.user_id
            )
            at_player_name = (
                at_player_name["card"]
                if at_player_name["card"]
                else at_player_name["nickname"]
            )
            self._current_player[event.group_id] = {}
            return Message(
                f"{MessageSegment.at(self._current_player[event.group_id][1])}\n"
                f"{at_player_name}拒绝了你的对决！"
            )

    def settlement(self, event: GroupMessageEvent) -> str:
        """
        结算检测
        :param event: event
        """
        self._init_player_data(event)
        if (
            not self._current_player.get(event.group_id)
            or self._current_player[event.group_id][1] == 0
            or self._current_player[event.group_id][2] == 0
        ):
            return "比赛并没有开始...无法结算..."
        if (
            event.user_id != self._current_player[event.group_id][1]
            and event.user_id != self._current_player[event.group_id][2]
        ):
            return "吃瓜群众不要捣乱！黄牌警告！"
        if time.time() - self._current_player[event.group_id]["time"] <= 30:
            return (
                f'{self._current_player[event.group_id]["player1"]} '
                f'和 {self._current_player[event.group_id]["player2"]} 比赛并未超时，请继续比赛...'
            )
        win_name = (
            self._current_player[event.group_id]["player1"]
            if self._current_player[event.group_id][2]
            == self._current_player[event.group_id]["next"]
            else self._current_player[event.group_id]["player2"]
        )
        return f"这场对决是 {win_name} 胜利了"

    async def check_current_game(
        self, bot: Bot, event: GroupMessageEvent
    ) -> Optional[str]:
        """
        检查当前是否有决斗存在
        """
        self._init_player_data(event)
        if (
            self._current_player[event.group_id][1]
            and not self._current_player[event.group_id][2]
            and time.time() - self._current_player[event.group_id]["time"] <= 30
        ):
            return f'现在是 {self._current_player[event.group_id]["player1"]} 发起的对决\n请等待比赛结束后再开始下一轮...'
        if (
            self._current_player[event.group_id][1]
            and self._current_player[event.group_id][2]
            and time.time() - self._current_player[event.group_id]["time"] <= 30
        ):
            return (
                f'{self._current_player[event.group_id]["player1"]} 和'
                f' {self._current_player[event.group_id]["player2"]}的对决还未结束！'
            )
        if (
            self._current_player[event.group_id][1]
            and self._current_player[event.group_id][2]
            and time.time() - self._current_player[event.group_id]["time"] > 30
        ):
            await bot.send(event, message="决斗已过时，强行结算...")
            await self.end_game(bot, event)
        if (
            not self._current_player[event.group_id][2]
            and time.time() - self._current_player[event.group_id]["time"] > 30
        ):
            self._current_player[event.group_id][1] = 0
            self._current_player[event.group_id][2] = 0
            self._current_player[event.group_id]["at"] = 0
        return None

    def ready_game(
        self,
        event: GroupMessageEvent,
        msg: str,
        player1_name: str,
        at_: int,
        money: int,
        bullet_num: int,
    ) -> Message:
        """
        发起游戏
        :param event: event
        :param msg: 提示消息
        :param player1_name: 玩家
        :param at_: at用户
        :param money: 赌注金额
        :param bullet_num: 装填子弹数量
        """
        self._current_player[event.group_id] = {
            1: event.user_id,
            "player1": player1_name,
            2: 0,
            "player2": "",
            "at": at_,
            "next": event.user_id,
            "money": money,
            "bullet": random_bullet(bullet_num),
            "bullet_num": bullet_num,
            "null_bullet_num": 7 - bullet_num,
            "index": 0,
            "time": time.time(),
        }
        return Message(
            ("咔 " * bullet_num)[:-1] + f"，装填完毕\n挑战金额：{money}\n"
            f"第一枪的概率为：{str(float(bullet_num) / 7.0 * 100)[:5]}%\n"
            f"{msg}"
        )

    async def shot(self, bot: Bot, event: GroupMessageEvent, count: int):
        """
        开枪！！！
        :param bot: bot
        :param event: event
        :param count: 开枪次数
        """
        check_message = await self._shot_check(bot, event)
        if check_message:
            await bot.send(event, check_message)
            return
        player1_name = self._current_player[event.group_id]["player1"]
        player2_name = self._current_player[event.group_id]["player2"]
        current_index = self._current_player[event.group_id]["index"]
        _tmp = self._current_player[event.group_id]["bullet"][
            current_index : current_index + count
        ]
        if 1 in _tmp:
            flag = _tmp.index(1) + 1
        else:
            flag = -1
        if flag == -1:
            next_user = MessageSegment.at(
                self._current_player[event.group_id][1]
                if event.user_id == self._current_player[event.group_id][2]
                else self._current_player[event.group_id][2]
            )
            # 概率
            x = str(
                float((self._current_player[event.group_id]["bullet_num"]))
                / float(
                    self._current_player[event.group_id]["null_bullet_num"]
                    - count
                    + self._current_player[event.group_id]["bullet_num"]
                )
                * 100
            )[:5]
            _msg = f"连开{count}枪，" if count > 1 else ""
            await bot.send(
                event,
                Message(
                    _msg
                    + random.choice(
                        [
                            "呼呼，没有爆裂的声响，你活了下来",
                            "虽然黑洞洞的枪口很恐怖，但好在没有子弹射出来，你活下来了",
                            f'{"咔 "*count}，你没死，看来运气不错',
                        ]
                    )
                    + f"\n下一枪中弹的概率"
                    f"：{x}%\n"
                    f"轮到 {next_user}了"
                ),
            )
            self._current_player[event.group_id]["null_bullet_num"] -= count
            self._current_player[event.group_id]["next"] = (
                self._current_player[event.group_id][1]
                if event.user_id == self._current_player[event.group_id][2]
                else self._current_player[event.group_id][2]
            )
            self._current_player[event.group_id]["time"] = time.time()
            self._current_player[event.group_id]["index"] += count
        else:
            await bot.send(
                event,
                random.choice(
                    [
                        '"嘭！"，你直接去世了',
                        "眼前一黑，你直接穿越到了异世界...(死亡)",
                        "终究还是你先走一步...",
                    ]
                )
                + f"\n第 {current_index + flag} 发子弹送走了你...",
                at_sender=True,
            )
            win_name = (
                player1_name
                if event.user_id == self._current_player[event.group_id][2]
                else player2_name
            )
            await asyncio.sleep(0.5)
            await bot.send(event, f"这场对决是 {win_name} 胜利了")
            await self.end_game(bot, event)

    async def _shot_check(self, bot: Bot, event: GroupMessageEvent) -> Optional[str]:
        """
        开枪前检查游戏是否合法
        :param bot: bot
        :param event: event
        """
        try:
            if time.time() - self._current_player[event.group_id]["time"] > 30:
                if self._current_player[event.group_id][2] == 0:
                    self._current_player[event.group_id][1] = 0
                    return "这场对决已经过时了，请重新装弹吧！"
                else:
                    await bot.send(event, "决斗已过时，强行结算...")
                    await self.end_game(bot, event)
                    return None
        except KeyError:
            return "目前没有进行的决斗，请发送 装弹 开启决斗吧！"
        if self._current_player[event.group_id][1] == 0:
            return "没有对决，也还没装弹呢，请先输入 装弹 吧！"
        if (
            self._current_player[event.group_id][1] == event.user_id
            and self._current_player[event.group_id][2] == 0
        ):
            return "baka，你是要枪毙自己嘛笨蛋！"
        if self._current_player[event.group_id][2] == 0:
            return "请这位勇士先发送 接受对决 来站上擂台..."
        player1_name = self._current_player[event.group_id]["player1"]
        player2_name = self._current_player[event.group_id]["player2"]
        if self._current_player[event.group_id]["next"] != event.user_id:
            if (
                event.user_id != self._current_player[event.group_id][1]
                and event.user_id != self._current_player[event.group_id][2]
            ):
                nickname = (
                    event.sender.card if event.sender.card else event.sender.nickname
                )
                return random.choice(
                    [
                        f"不要打扰 {player1_name} 和 {player2_name} 的决斗啊！",
                        f"给我好好做好一个观众！不然本裁判就要生气了",
                        f"不要捣乱啊baka{nickname}！",
                    ]
                )
            nickname = (
                player1_name
                if self._current_player[event.group_id]["next"]
                == self._current_player[event.group_id][1]
                else player2_name
            )
            return f"你的左轮不是连发的！该 {nickname} 开枪了"
        return None

    def get_user_data(self, event: GroupMessageEvent) -> Dict[str, Union[str, int]]:
        """
        获取用户数据
        :param event:
        :return:
        """
        self._init_player_data(event)
        return self._player_data[str(event.group_id)][str(event.user_id)]

    def get_current_bullet_index(self, event: GroupMessageEvent) -> int:
        """
        获取当前剩余子弹数量
        :param event: event
        """
        return self._current_player[event.group_id]["index"]

    async def rank(self, msg: str, group_id: int) -> str:
        """
        获取排行榜
        :param msg: 排行榜类型
        :param group_id: 群号
        """
        msg = msg.strip()
        if msg in ["胜场排行", "胜利排行", "胜场排名", "胜利排名"]:
            return await rank(self._player_data, group_id, "win_rank")
        if msg in ["败场排行", "失败排行", "败场排名", "失败排名"]:
            return await rank(self._player_data, group_id, "lose_rank")
        if msg == "欧洲人排行":
            return await rank(self._player_data, group_id, "make_gold")
        if msg == "慈善家排行":
            return await rank(self._player_data, group_id, "lose_gold")

    def check_game_is_start(self, group_id: int) -> bool:
        """
        检测群内游戏是否已经开始
        :param group_id: 群号
        """
        return self._current_player[group_id][1] != 0

    def save(self):
        """
        保存数据
        """
        with open(self.file, "w", encoding="utf8") as f:
            json.dump(self._player_data, f, ensure_ascii=False, indent=4)

    def _init_player_data(self, event: GroupMessageEvent):
        """
        初始化用户数据
        :param event: event
        """
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        if group_id not in self._player_data.keys():
            self._player_data[group_id] = {}
        if user_id not in self._player_data[group_id].keys():
            self._player_data[group_id][user_id] = {
                "user_id": user_id,
                "group_id": group_id,
                "nickname": nickname,
                "gold": 0,
                "make_gold": 0,
                "lose_gold": 0,
                "win_count": 0,
                "lose_count": 0,
                "is_sign": False,
            }

    async def end_game(self, bot: Bot, event: GroupMessageEvent):
        """
        游戏结束结算
        :param bot: Bot
        :param event: event
        :return:
        """
        player1_name = self._current_player[event.group_id]["player1"]
        player2_name = self._current_player[event.group_id]["player2"]
        if (
            self._current_player[event.group_id]["next"]
            == self._current_player[event.group_id][1]
        ):
            win_user_id = self._current_player[event.group_id][2]
            lose_user_id = self._current_player[event.group_id][1]
            win_name = player2_name
            lose_name = player1_name
        else:
            win_user_id = self._current_player[event.group_id][1]
            lose_user_id = self._current_player[event.group_id][2]
            win_name = player1_name
            lose_name = player2_name
        rand = random.randint(0, 5)
        gold = self._current_player[event.group_id]["money"]
        fee = int(gold * float(rand) / 100)
        fee = 1 if fee < 1 and rand != 0 else fee
        self._end_data_handle(win_user_id, lose_user_id, event.group_id, gold, fee)
        win_user = self._player_data[str(event.group_id)][str(win_user_id)]
        lose_user = self._player_data[str(event.group_id)][str(lose_user_id)]
        bullet_str = ""
        for x in self._current_player[event.group_id]["bullet"]:
            bullet_str += "__ " if x == 0 else "| "
        logger.info(f"俄罗斯轮盘：胜者：{win_name} - 败者：{lose_name} - 金币：{gold}")
        self._current_player[event.group_id] = {}
        await bot.send(
            event,
            message=f"结算：\n"
            f"\t胜者：{win_name}\n"
            f"\t赢取金币：{gold - fee}\n"
            f'\t累计胜场：{win_user["win_count"]}\n'
            f'\t累计赚取金币：{win_user["make_gold"]}\n'
            f"-------------------\n"
            f"\t败者：{lose_name}\n"
            f"\t输掉金币：{gold}\n"
            f'\t累计败场：{lose_user["lose_count"]}\n'
            f'\t累计输掉金币：{lose_user["lose_gold"]}\n'
            f"-------------------\n"
            f"哼哼，{bot_name}从中收取了 {float(rand)}%({fee}金币) 作为手续费！\n"
            f"子弹排列：{bullet_str[:-1]}",
        )

    def _end_data_handle(
        self,
        win_user_id: int,
        lose_user_id,
        group_id: int,
        gold: int,
        fee: int,
    ):
        """
        结算数据处理保存
        :param win_user_id: 胜利玩家id
        :param lose_user_id: 失败玩家id
        :param group_id: 群聊
        :param gold: 赌注金币
        :param fee: 手续费
        """
        win_user_id = str(win_user_id)
        lose_user_id = str(lose_user_id)
        group_id = str(group_id)
        cursor.execute(f"SELECT credit FROM credit WHERE gid='{group_id}' AND uid='{win_user_id}';")
        win_source_gold = cursor.fetchone()[0]

        cursor.execute(
            f'''UPDATE credit SET credit={win_source_gold + gold - fee} WHERE uid='{win_user_id}' AND gid='{group_id}';'''
        )

        self._player_data[group_id][win_user_id]["make_gold"] += gold - fee
        self._player_data[group_id][win_user_id]["win_count"] += 1

        cursor.execute(f"SELECT credit FROM credit WHERE gid='{group_id}' AND uid='{lose_user_id}';")
        lose_source_gold = cursor.fetchone()[0]
        self._player_data[group_id][lose_user_id]["lose_gold"] += gold
        self._player_data[group_id][lose_user_id]["lose_count"] += 1

        cursor.execute(
            f'''UPDATE credit SET credit={lose_source_gold - gold} WHERE uid='{lose_user_id}' AND gid='{group_id}';'''
        )

        self.save()


russian_manager = RussianManager()
