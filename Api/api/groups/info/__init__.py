from fastapi import Depends, FastAPI, Body
from nonebot import get_app, get_bot
from nonebot.adapters.onebot.v11 import Bot
from ...model import Result, Group, User
from ...utils import auth
from utils import path, json_tools, init, users


app: FastAPI = get_app()


@app.post("/api/groups/info/groups_info", response_model=Result, dependencies=[Depends(auth)])
async def groups_info() -> Result:
    bot: Bot = get_bot()
    group_list: list = await bot.get_group_list()
    data = {}
    for group_detail in group_list:
        group_id = str(group_detail["group_id"])
        enable = (await json_tools.json_load_async(path.enable_config_path)).get(group_id)
        enable = enable if enable is not None else False
        data.update({
            group_id: {
                **group_detail,
                "enable": enable
            }
        })
    return Result(data=data)


@app.post("/api/groups/info/group_info", response_model=Result, dependencies=[Depends(auth)])
async def group_info(group: Group) -> Result:
    bot: Bot = get_bot()
    group_detail: dict = await bot.get_group_info(group_id=int(group.group_id))
    enable = (await json_tools.json_load_async(path.enable_config_path)).get(group.group_id)
    enable = enable if enable is not None else False
    group_detail.update({"enable": enable})
    return Result(data=group_detail)


@app.post("/api/groups/info/group_members", response_model=Result, dependencies=[Depends(auth)])
async def group_members(group: Group) -> Result:
    bot: Bot = get_bot()
    group_member_list: list = await bot.get_group_member_list(group_id=int(group.group_id))
    for member in group_member_list:
        uid = str(member.get("user_id"))
        gid = group.group_id
        member.update({
            "role": users.get_role(gid, uid),
            "ban_count": users.get_ban_count(uid, gid),
            "sign_date_last": users.get_dateLast(gid, uid),
            "sign_count_all": users.get_countAll(gid, uid),
            "sign_count_continue": users.get_countContinue(gid, uid),
            "credit": users.get_credit(gid, uid),
        })
    data: dict = {
        "members": group_member_list
    }
    return Result(data=data)


@app.post("/api/groups/info/group_member", response_model=Result, dependencies=[Depends(auth)])
async def group_member(group: Group, user: User) -> Result:
    bot: Bot = get_bot()
    uid = user.user_id
    gid = group.group_id
    group_member_detail: dict = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
    group_member_detail.update({
        "role": users.get_role(gid, uid),
        "ban_count": users.get_ban_count(uid, gid),
        "sign_date_last": users.get_dateLast(gid, uid),
        "sign_count_all": users.get_countAll(gid, uid),
        "sign_count_continue": users.get_countContinue(gid, uid),
        "credit": users.get_credit(gid, uid),
    })
    return Result(data=group_member_detail)


@app.post("/api/groups/info/group_member_bot", response_model=Result, dependencies=[Depends(auth)])
async def group_member_bot(group: Group) -> Result:
    bot: Bot = get_bot()
    uid = bot.self_id
    gid = group.group_id
    group_member_detail: dict = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
    group_member_detail.update({
        "ban_count": users.get_ban_count(uid, gid),
        "sign_date_last": users.get_dateLast(gid, uid),
        "sign_count_all": users.get_countAll(gid, uid),
        "sign_count_continue": users.get_countContinue(gid, uid),
        "credit": users.get_credit(gid, uid),
    })
    return Result(data=group_member_detail)


@app.post("/api/groups/info/group_enable", response_model=Result, dependencies=[Depends(auth)])
async def group_enable(group: Group) -> Result:
    await json_tools.json_update_async(path.enable_config_path, group.group_id, True)
    return Result(0)


@app.post("/api/groups/info/group_disable", response_model=Result, dependencies=[Depends(auth)])
async def group_disable(group: Group) -> Result:
    await json_tools.json_update_async(path.enable_config_path, group.group_id, False)
    return Result(0)


@app.post("/api/groups/info/group_init", response_model=Result, dependencies=[Depends(auth)])
async def group_init(group: Group) -> Result:
    await init(get_bot(), group.group_id)
    return Result(0)