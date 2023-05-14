from fastapi import Depends, FastAPI, Body
from nonebot import get_app
from ...model import Result, Group, User
from ...utils import auth
from ...exception import ParamError
from utils import users, permission


app: FastAPI = get_app()


@app.post("/api/groups/user/update_role", response_model=Result, dependencies=[Depends(auth)])
async def update_role(group: Group, user: User) -> Result:
    if not user.role:
        raise ParamError
    if user.role not in permission.permissions:
        return Result(102, "权限不存在")
    user_role = users.get_role(group.group_id, user.user_id)
    if user_role in ["admin", "owner", "Van"]:
        return Result(102, f"用户权限 {user_role} 不可修改")
    users.update_role(group.group_id, user.user_id, user.role)
    return Result(0)


@app.post("/api/groups/user/update_credit", response_model=Result, dependencies=[Depends(auth)])
async def update_credit(group: Group, user: User) -> Result:
    try:
        if not user.credit is None:
            raise ParamError
        if int(user.credit) < 0:
            return Result(102, "积分数不能为负数")
        users.set_credit(group.group_id, user.user_id, int(user.credit))
        return Result(0)
    except ValueError:
        return Result(102, "积分应为整数")


@app.post("/api/groups/user/update_ban_count", response_model=Result, dependencies=[Depends(auth)])
async def update_ban_count(group: Group, user: User) -> Result:
    try:
        if user.ban_count is None:
            raise ParamError
        if int(user.ban_count) < 0:
            return Result(102, "次数不能为负数")
        users.set_ban_count(user.user_id, group.group_id, user.ban_count)
        return Result(0)
    except ValueError:
        return Result(102, "积分应为整数")


@app.post("/api/groups/user/update_sign", response_model=Result, dependencies=[Depends(auth)])
async def update_sign(group: Group, user: User) -> Result:
    try:
        date_last = users.update_dateLast(group.group_id, user.user_id, user.sign_date_last) if user.sign_date_last is not None else 1
        count_all = users.update_countAll(group.group_id, user.user_id, user.sign_count_all) if user.sign_count_all is not None else 1
        count_continue = users.update_countContinue(group.group_id, user.user_id, user.sign_count_continue) if user.sign_count_continue else 1
        
        if date_last and count_all and count_continue:
            return Result(0)
        else:
            return Result(101, "修改失败")
    except ValueError:
        return Result(102, "日期格式不正确")


@app.post("/api/groups/user/update_info", response_model=Result, dependencies=[Depends(auth)])
async def update_info(group: Group, user: User) -> Result:
    if user.credit is None or user.ban_count is None or user.sign_count_all is None or user.sign_count_continue is None or not user.sign_date_last or not user.role:
        raise ParamError

    users.update_role(group.group_id, user.user_id, user.role)
    users.set_credit(group.group_id, user.user_id, int(user.credit))
    users.set_ban_count(user.user_id, group.group_id, user.ban_count)
    users.update_dateLast(group.group_id, user.user_id, user.sign_date_last)
    users.update_countAll(group.group_id, user.user_id, user.sign_count_all)
    users.update_countContinue(group.group_id, user.user_id, user.sign_count_continue)
    return Result(0)
