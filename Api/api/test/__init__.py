import jwt
from nonebot import get_app
from fastapi import FastAPI, Body, Depends
from ..model import Result
from ..utils import auth, secret_key

app: FastAPI = get_app()

@app.post("/api/test/decode", response_model=Result)
async def login_auth(token=Body(None)) -> Result:
    try:
        decode = jwt.decode(token, secret_key, algorithms=["HS256"])
        return Result(0, data={"decode": decode})
    except jwt.exceptions.ExpiredSignatureError:
        return Result(102, "token已过期")
    except Exception as e:
        return Result(-1, str(e))


@app.post("/api/test/connection", response_model=Result)
async def connect_test() -> Result:
    return Result(0)


@app.post("/api/test/auth_token", response_model=Result, dependencies=[Depends(auth)])
async def auth_token_test() -> Result:
    return Result(0, msg="身份验证成功")
    