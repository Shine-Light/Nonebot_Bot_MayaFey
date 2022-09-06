"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/30 13:04
"""
from utils import database_mysql
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message
from nonebot.params import CommandArg, Arg
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
from nonebot.log import logger


# /sql 代码
execSql = on_command(cmd="sql", aliases={"Sql", "SQL"}, priority=5, permission=SUPERUSER)
@execSql.handle()
async def _(event: PrivateMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent):
        if args.extract_plain_text():
            matcher.set_arg(key="sql", message=args)


@execSql.got(key="sql", prompt="请发送SQL代码")
async def _(event: PrivateMessageEvent, matcher: Matcher):
    sql = matcher.get_arg("sql").extract_plain_text()
    try:
        database_mysql.cursor.execute(sql)
        await execSql.finish(Message(f"查询结果\n{database_mysql.cursor.fetchall()}"))
    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"Sql查询出错:{str(e)}")
        await execSql.finish(f"出现错误:f{e}")

