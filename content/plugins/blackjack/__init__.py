from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.params import Message, CommandArg
from nonebot.plugin import PluginMetadata
from .game import get_point, add_game, start_game, call_card, stop_card, get_game_ls, duel #, get_rank
from typing import Dict, List
from utils.other import add_target


msg_help = '''黑杰克帮助:
发起游戏: /21点 {积分}
查看游戏列表: /21点列表
加入游戏: /21点加入 {游戏ID}
叫牌: /叫牌 {游戏ID}
停牌: /停牌 {游戏ID}
对战(自动进行): /21点对战 {积分} @某人
接收对战: /21点接受对战 {游戏ID}
查看对战列表: /21点对战列表
可以有多场游戏,也可以同时进行多场游戏''' + add_target(60)


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="blackjack",
    description="21点又名黑杰克,一种扑克牌玩法",
    usage=msg_help,
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "yaowan233",
        "translate": "21点",
    }
)


menu = on_command("黑杰克帮助", aliases={"21点帮助"}, priority=7)
blackjack = on_command("21点", aliases={"发起21点", '发起黑杰克', '黑杰克'}, priority=7, block=False)
accept_blackjack = on_command("21点加入", aliases={'21点接受', '黑杰克加入', '黑杰克接受'}, priority=7, block=False)
blackjack_list = on_command("21点列表", aliases={'黑杰克列表'}, priority=7, block=False)
call = on_command("叫牌", aliases={'call'}, priority=7, block=False)
stop = on_command("停牌", aliases={'stop'}, priority=7, block=False)
point_battle = on_command("21点对战", aliases={"黑杰克对战", "发起21点对战"}, priority=7, block=False)
accept_battle = on_command("21点接受对战", aliases={"黑杰克接受对战"}, priority=7, block=False)
battle_list = on_command("21点对战列表", aliases={"黑杰克对战列表"}, priority=7, block=False)
# rank = on_command("rank", aliases={'排名'})
battle_dic: Dict[int, List[List[int]]] = {}


@blackjack.handle()
async def start_blackjack(event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.user_id
    if msg.extract_plain_text() in ["帮助", "help"]:
        await blackjack.finish(msg_help)
    point = msg.extract_plain_text().strip()
    player1_name = event.sender.card or event.sender.nickname
    if not point.isdigit():
        await blackjack.finish("请输入正确的积分数！")
    point = int(point)
    user_point = get_point(group_id, user_id)
    if user_point < point:
        await blackjack.finish("你的积分不够！")
    deck_id = await add_game(group_id, user_id, point, player1_name)
    if deck_id >= 0:
        await blackjack.finish(f"游戏添加成功 游戏id为{deck_id}")
    else:
        await blackjack.finish("出错了QwQ 对战添加失败")


@accept_blackjack.handle()
async def accept(event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.user_id
    battle_id = msg.extract_plain_text().strip()
    player2_name = event.sender.card or event.sender.nickname
    user_point = get_point(group_id, user_id)
    if not battle_id.isdigit():
        await accept_blackjack.finish("请输入正确的游戏id！", at_sender=True)
    words = await start_game(int(battle_id), user_id, player2_name, group_id, user_point)
    await accept_blackjack.finish(words, at_sender=True)


@call.handle()
async def _call(event: GroupMessageEvent, msg: Message = CommandArg()):
    user_id = event.user_id
    deck_id = msg.extract_plain_text().strip()
    if not deck_id.isdigit():
        await call.finish("请输入正确的游戏id！", at_sender=True)
    words = await call_card(int(deck_id), user_id)
    await call.finish(words, at_sender=True)


@stop.handle()
async def _stop(event: GroupMessageEvent, msg: Message = CommandArg()):
    user_id = event.user_id
    deck_id = msg.extract_plain_text().strip()
    if not deck_id.isdigit():
        await call.finish("请输入正确的游戏id！", at_sender=True)
    words = await stop_card(int(deck_id), user_id)
    await stop.finish(words, at_sender=True)


@blackjack_list.handle()
async def accept(event: GroupMessageEvent):
    group_id = event.group_id
    words = await get_game_ls(group_id)
    await blackjack.finish(words)


@point_battle.handle()
async def battle(event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.user_id
    point = msg.extract_plain_text().strip()
    if not point.isdigit():
        await point_battle.finish("请输入数字！")
    point = int(point)
    user_point = get_point(group_id, user_id)
    if user_point < point:
        await point_battle.finish("你的积分不够！")
    battle_id = add_dual(group_id, user_id, point)
    if battle_id >= 0:
        await point_battle.finish(f"对战添加成功 对战id为{battle_id}")
    else:
        await point_battle.finish("出错了QwQ 对战添加失败")


@accept_battle.handle()
async def accept(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.group_id
    acceptor = event.user_id
    acceptor_name = event.sender.card or event.sender.nickname
    battle_id = msg.extract_plain_text().strip()
    if not battle_id.isdigit():
        await point_battle.finish("请输入对战的数字id！")
    battle_id = int(battle_id)
    battle_info = get_battle_info(group_id, battle_id)
    if not battle_info:
        await point_battle.finish("对战id不存在！")
        return
    (battle_id, challenger, point) = battle_info
    acceptor_point = get_point(group_id, acceptor)
    challenger_point = get_point(group_id, challenger)
    sender = await bot.get_group_member_info(group_id=group_id, user_id=challenger)
    challenger_name = sender['card'] or sender.get('nickname', '')
    if acceptor_point < point:
        await point_battle.finish("你的积分不够！")
    if acceptor == challenger:
        await point_battle.finish("不能和自己对战！")
    words = duel(group_id, point, challenger, challenger_point, challenger_name,
                 acceptor, acceptor_point, acceptor_name)
    for index, battle_ls in enumerate(battle_dic[group_id]):
        if battle_ls[0] == battle_id:
            del battle_dic[group_id][index]
            break
    await accept_battle.finish(words)


@battle_list.handle()
async def accept(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    if group_id not in battle_dic:
        await battle_list.finish("没有进行中的对战\n使用 /发起对战 积分 发起一个吧")
    s = ""
    for battle_id, uid, point in battle_dic[group_id]:
        sender = await bot.get_group_member_info(group_id=group_id, user_id=uid)
        name = sender['card'] or sender.get('nickname', '')
        s += f"{battle_id} 发起人:{name} 对战积分:{point}\n"
    s = s[:-1]
    await battle_list.finish(s)


def add_dual(group: int, uid: int, point: int) -> int:
    if group not in battle_dic or not battle_dic[group]:
        battle_dic[group] = [[1, uid, point]]
        return 1
    battle_id = battle_dic[group][-1][0] + 1
    battle_dic[group].append([battle_id, uid, point])
    return battle_id


def get_battle_info(group: int, battle_id: int) -> list:
    if group not in battle_dic or battle_id <= 0:
        return []
    for i in battle_dic[group]:
        if i[0] == battle_id:
            return i
    return []


# @rank.handle()
# async def main(bot: Bot, event: GroupMessageEvent):
#     group_id = event.group_id
#     msg = await get_rank(group_id, bot)
#     await rank.finish(msg)
