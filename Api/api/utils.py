"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/4 20:36
"""
import datetime
import jwt
from typing import Optional
from nonebot import get_driver
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from fastapi.exceptions import HTTPException
from utils.config import manager
from .exception import AuthError


secret_key = "wzQ73awPw7UJN9n9"
driver = get_driver()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


async def auth(token: str = Depends(oauth2_scheme)):
    if token and token in await get_tokens():
        try:
            payload = await decode_token(token)
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthError
        if payload.get("username"):
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise AuthError
    else:
        raise AuthError


async def passwordAuth(username: Optional[str], password: Optional[str]) -> tuple[bool, Optional[str]]:
    if not username or not password:
        return False, None
    users: list = manager.getPluginConfig('api').get_config_general('users')
    for user in users:
        if user['username'] == username and password == user['password']:
            token = await create_token(username)
            return True, token
    return False, None


async def decode_token(token: str):
    return jwt.decode(token, secret_key, algorithms=["HS256"])


async def add_token(token: str):
    tokens: list = await get_tokens()
    tokens.append(token)
    config = manager.getPluginConfig("api")
    config.set_config_general("tokens", tokens)


async def clean_token():
    tokens = await get_tokens()
    for token in set(tokens):
        try:
            if await decode_token(token):
                continue
        except jwt.exceptions.ExpiredSignatureError:
            tokens.remove(token)
    config = manager.getPluginConfig("api")
    config.set_config_general("tokens", tokens)

async def create_token(username: str):
    expire_time = manager.getPluginConfig('api').get_config_general('expire')
    payload = {
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=expire_time),
        "username": username
    }
    token = jwt.encode(payload, secret_key, "HS256")
    await add_token(token)
    return token


async def get_tokens() -> list:
    config = manager.getPluginConfig("api")
    return config.get_config_general("tokens")
