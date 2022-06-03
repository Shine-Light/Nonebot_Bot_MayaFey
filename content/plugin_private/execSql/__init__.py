"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/30 13:04
"""
import json

import nonebot

from utils import database_mysql, users
from content.plugins.permission.tools import permission_
from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message, Event, NoticeEvent
from nonebot.params import CommandArg, Received
from nonebot.exception import FinishedException

config = nonebot.get_driver().config

# /sql gid
execSql = on_command(cmd="sql", aliases={"Sql", "SQL"}, priority=5)
@execSql.handle()
async def _(event: Event, args: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent):
        uid = str(event.user_id)
        args = args.extract_plain_text()

        sep = " "
        for i in config.command_sep:
            sep = i
        cmds = args.split(str(sep))

        gid = cmds[0]

        if not permission_(users.get_role(gid, uid), "admin"):
            try:
                await execSql.finish("您无该群的 管理员及以上 的权限")
            except FinishedException:
                pass

        await execSql.send("验证成功,请发送SQL文件/代码")


@execSql.receive("sql")
async def _(event: Event = Received("sql")):
    sql = event.get_plaintext()
    try:
        upcase = sql.upper()
        # 禁用关键字
        for i in ["ALTER", "DELETE", "CREATE", "INSERT", "DROP", "TRUNCATE", "UPDATE"]:
            if i in upcase:
                await execSql.finish(f"不允许 {i} 关键字")
        database_mysql.cursor.execute(sql)
        await execSql.finish(Message(f"查询结果\n{database_mysql.cursor.fetchall()}"))
    except FinishedException:
        pass
    except Exception as e:
        await execSql.finish(f"出现错误:f{e}")

