"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/22 20:39
"""

import json
import asyncio

from nonebot import on_command, on_notice, on_message
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent
from nonebot.rule import Rule, to_me
from nonebot import get_driver
from ..withdraw import add_target
from .. import update


# 戳一戳检测规则
def checker_click():
    async def _checker(bot: Bot, event: Event) -> bool:
        description = event.get_event_description()
        values = json.loads(description.replace("'", '"'))
        if values['notice_type'] == 'notify' and values['sub_type'] == 'poke' and values['target_id'] == values['self_id']:
            return True

    return Rule(_checker)


# 机器人id
bot_id = get_driver().config.bot_id
loop = asyncio.get_event_loop()

message_main: str = '''你好!我是真宵,让我来告诉如何使用机器人吧
命令提示:空格表示命令别名分隔,{}为自主输入的参数
[]为可选参数,"|"表示或者,()中为补充内容,其余符号都是指令内容
群成员所有命令在10s内只能触发5次,超过五次就禁言5min
总菜单: 艾特我 戳一戳我 /帮助
娱乐菜单: /娱乐菜单
游戏存档: /游戏菜单
生活菜单: /生活菜单
管理菜单: /管理菜单
积分菜单: /积分菜单
权限菜单: /权限菜单
问答菜单: /问答菜单
关于本项目: /关于
机器人版本:%s
出现问题请找开发
开发:Shine_Light(3120815902)'''

message_fun: str = '''这是娱乐菜单
每日一签: /签到 /打卡
一句一言: /一言
随机图片: /图片[二次元图片(不填默认)|头像|Bing]
全网热搜: /热搜(天行数据版本)
        /热搜 [知乎/百度/B站/历史今天/贴吧/IT]
随机笑话: /笑话
点歌: /网易|酷我|酷狗|b站|qq(默认)点歌 {歌名}
群词云: /群词云
logo生成: /logo 帮助
表情包生成: /表情包制作
答案之书: 翻看答案{问题}''' + add_target(60)

# message_fun: str = '''这是娱乐菜单
# 每日一签: /签到 /打卡
# 一句一言: /一言
# 随机图片: /图片[二次元图片(不填默认)|头像|Bing]
# 全网热搜: /热搜 [知乎|百度|B站|历史今天|贴吧|微博|IT]
# 随机笑话: /笑话
# 点歌: /网易|酷我|酷狗|b站|qq(默认)点歌 {歌名}
# 群词云: /群词云
# logo生成: /logo 帮助
# 表情包生成: /表情包制作''' + add_target(60)

message_life: str = '''这是生活菜单
翻译: /翻译
疫情查询: 
    {城市名}疫情
    {城市名}疫情政策
    {城市名}风险地区
天气: {城市名}天气
违禁词查询: /违禁词 列表
Epic限免资讯: /Epic喜加一 
        /喜加一订阅 (>=超级用户)''' + add_target(60)

message_admin: str = '''这是管理菜单
管理命令中有空格的要加空格,@后自带空格所以可以不用再加
[超级用户及以上]
机器人更新:
    /检查更新
    /更新
    /更新日志
疫情关注(18:30推送)
    /关注疫情 {城市名}
    /取消关注疫情 {城市名}
    /疫情关注列表
解|禁言(可批量)
    /禁@某人 @某人 {时间}(单位:s 范围:1~25919999 不加则随机)
    /解@某人 @某人
踢出|踢出并拉黑(可批量)
    /踢@某人 @某人
    /黑@某人 @某人
群词云(19:00推送)
    /记录本群
    /停止记录本群
违禁词
    /简单违禁词
    /严格违禁词
    /更新违禁词库(每周自动执行)
插件开关
    /开关状态
    /开关{功能名}
入群|回群欢迎
    /入群欢迎 {内容}
    /回群欢迎 {内容}
插件统计
    /插件统计
插件控制
    /插件控制 {插件名}
    /插件控制 状态''' + add_target(60)


message_credit: str = '''这是积分系统菜单
查看当前积分: /积分 /我的积分
排行榜(前十): /积分排行榜 /积分排名
积分获取方式: 签到(积分随天数累加) 小游戏''' + add_target(60)


message_permission: str = '''这是权限菜单
权限: 群主>群管理>超级用户>群成员>黑名单
权限(英文): owner>admin>superuser>member>baned
查看自己权限: /我的权限
设置权限(管理员及以上): /权限设置 @某人 {权限名(英|中)}''' + add_target(60)


message_question: str = '''这是自定义问答菜单
添加问答(超级用户及以上):
    精准问{检测关键词}答{回答内容}
    模糊问{检测关键词}答{回答内容}
删除问答(超级用户及以上):
    /问答删除 {问题}
查看问题列表(成员及以上):
    /问答列表''' + add_target(60)

message_games: str = '''这是游戏菜单
游戏的帮助菜单命令为 '/游戏名 帮助'
游戏列表:
    俄罗斯轮盘
    黑杰克(21点)''' + add_target(60)

message_about: str = '''关于这个项目:
该项目纯兴趣开发,旨在学习和参考,请勿用于非法用途和盈利
开发者现在高中在读,学业限制,开发进度较缓
项目地址(未开放):''' + add_target(60)


# 总菜单
main = on_command(cmd="菜单", aliases={"help", "帮助"}, priority=9)
@main.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    version = loop.run_until_complete(update.tools.get_version())
    await bot.send(event=event,
                   message=message_main % version + add_target(60))

# 总菜单戳一戳
main_click = on_notice(rule=checker_click(), priority=9)
@main_click.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_main)

# 总菜单 @
main_at = on_message(rule=to_me(), priority=9)
@main_at.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message_meta: str = str(event.get_message())
    if message_meta == '':
        await bot.send(event=event,
                       message=message_main)


# 娱乐菜单
fun = on_command(cmd="娱乐菜单", aliases={"fun"}, priority=9)
@fun.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_fun)

# 生活菜单
life = on_command(cmd="生活菜单", aliases={"life"}, priority=9)
@life.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_life)

# 管理菜单
admin = on_command(cmd="管理菜单", aliases={"admin"}, priority=9)
@admin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_admin)

# 积分菜单
credit = on_command(cmd="积分菜单", aliases={"credit_menu"}, priority=9)
@credit.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_credit)


# 权限菜单
permission = on_command(cmd="权限菜单", aliases={"permission_menu"}, priority=9)
@permission.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_permission)


# 问答菜单
question = on_command(cmd="问答菜单", aliases={"question_menu"}, priority=9)
@question.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_question)

# 游戏菜单
games = on_command(cmd="游戏菜单", aliases={"games_menu"}, priority=9)
@games.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_games)

# 关于
games = on_command(cmd="关于", aliases={"about"}, priority=9)
@games.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.send(event=event,
                   message=message_about)
