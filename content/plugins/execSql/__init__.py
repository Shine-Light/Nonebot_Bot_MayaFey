"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/5/30 13:04
"""
import nonebot

from utils import database_mysql, users
from content.plugins.permission.tools import permission_
from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message, Event, NoticeEvent
from nonebot.params import CommandArg, Received
from nonebot.exception import FinishedException
from nonebot.typing import T_State

config = nonebot.get_driver().config

# /sql gid txt\file
execSql = on_command(cmd="sql", aliases={"Sql", "SQL"}, priority=5)
@execSql.handle()
async def _(event: Event, state: T_State, args: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent):
        uid = str(event.user_id)
        args = args.extract_plain_text()

        sep = " "
        for i in config.command_sep:
            sep = i
        cmds = args.split(str(i))

        gid = cmds[0]
        up_type = cmds[1]

        if not permission_(users.get_role(gid, uid), "admin"):
            try:
                await execSql.finish("您无该群的 管理员及以上 的权限")
            except FinishedException:
                pass

        await execSql.send("验证成功,请发送SQL文件/代码")
        if up_type == "file":
            execSql.set_receive(execSql, id="sql", event=event)

        state["up_type"] = up_type


@execSql.receive("sql")
async def _(state: T_State, event: Event = Received("sql")):
    up_type = state["up_type"]
    sql = event.get_plaintext()
    if up_type != "file":
        try:
            database_mysql.cursor.execute(sql)
            await execSql.finish(Message(f"查询结果\n{database_mysql.cursor.fetchall()}"))
        except FinishedException:
            pass
        except Exception as e:
            await execSql.finish(f"出现错误:f{e}")
    else:
        pass


@execSql.type_updater
async def _(state: T_State):
    if state["up_type"] == "file":
        return "notice"


@execSql.receive("sql")
async def _(state: T_State, event: NoticeEvent = Received("sql")):
    pass
