from nonebot import get_app
from fastapi import FastAPI, Body, Depends
from ..model import Result, LoginForm
from .. import utils

app: FastAPI = get_app()

@app.post("/api/login", response_model=Result)
async def login_auth(form: LoginForm) -> Result:
    """
    登陆验证, 登陆成功后会返回新token
    form: 登陆数据
    """
    success, token = await utils.passwordAuth(form.username, form.password)
    if success:
        return Result(0, "登陆成功", {"token": token})
    else:
        return Result(102, "用户名或密码错误!")


@app.post("/api/users/info", response_model=Result, dependencies=[Depends(utils.auth)])
async def users_info(token: str = Depends(utils.oauth2_scheme)) -> Result:
    return Result(0, data={
        "username": (await utils.decode_token(token))['username'],
        "roles": ['admin']
    })

