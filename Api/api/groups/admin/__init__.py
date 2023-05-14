from fastapi import Depends, FastAPI, Body
from nonebot import get_app, get_bot
from nonebot.adapters.onebot.v11 import Bot, ActionFailed
from ...model import Result, Group, Data, User
from ...utils import auth
from ...exception import ParamError
from utils import admin_tools
from utils import users as user_tools

app: FastAPI = get_app()

@app.post("/api/groups/admin/ban", response_model=Result, dependencies=[Depends(auth)])
async def ban(group: Group, data: Data) -> Result:
    users = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    await admin_tools.banSb(group.group_id, users, data.time)
    return Result(0)
    

@app.post("/api/groups/admin/unban", response_model=Result, dependencies=[Depends(auth)])
async def unban(group: Group, data: Data) -> Result:
    users = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    await admin_tools.banSb(group.group_id, users, 0)
    return Result(0)


@app.post("/api/groups/admin/ban_whole", response_model=Result, dependencies=[Depends(auth)])
async def ban_whole(group: Group) -> Result:
    if not group.group_id:
        raise ParamError
    await admin_tools.banWholeGroup(group.group_id, True)
    return Result(0)


@app.post("/api/groups/admin/unban_whole", response_model=Result, dependencies=[Depends(auth)])
async def unban_whole(group: Group) -> Result:
    if not group.group_id:
        raise ParamError
    await admin_tools.banWholeGroup(group.group_id, False)
    return Result(0)


@app.post("/api/groups/admin/kick", response_model=Result, dependencies=[Depends(auth)])
async def kick(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    await admin_tools.kick(group.group_id, users, False)
    return Result(0)


@app.post("/api/groups/admin/kick_block", response_model=Result, dependencies=[Depends(auth)])
async def kick_block(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    await admin_tools.kick(group.group_id, users, True)
    return Result(0)


@app.post("/api/groups/admin/title_set", response_model=Result, dependencies=[Depends(auth)])
async def title_set(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    bot: Bot = get_bot()
    for user in users:
        await bot.set_group_special_title(group_id=int(group.group_id), user_id=int(user), special_title=data.title, duration=-1)
    return Result(0)


@app.post("/api/groups/admin/title_unset", response_model=Result, dependencies=[Depends(auth)])
async def title_unset(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    bot: Bot = get_bot()
    for user in users:
        await bot.set_group_special_title(group_id=int(group.group_id), user_id=int(user), special_title="", duration=0)
    return Result(0)


@app.post("/api/groups/admin/admin_set", response_model=Result, dependencies=[Depends(auth)])
async def admin_set(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    bot: Bot = get_bot()
    for user in users:
        await bot.set_group_admin(group_id=int(group.group_id), user_id=int(user), enable=True)
        user_tools.update_role_with_check(group.group_id, user, "admin")
    return Result(0)


@app.post("/api/groups/admin/admin_unset", response_model=Result, dependencies=[Depends(auth)])
async def admin_unset(group: Group, data: Data) -> Result:
    users: list = data.users
    if isinstance(users, str) or isinstance(users, int):
        users = [users]
    bot: Bot = get_bot()
    for user in users:
        await bot.set_group_admin(group_id=int(group.group_id), user_id=int(user), enable=False)
        if user_tools.get_role(group.group_id, user) != "admin":
            user_tools.update_role_with_check(group.group_id, user, "member")
        else:
            user_tools.update_role(group.group_id, user, "member")
    return Result(0)
    