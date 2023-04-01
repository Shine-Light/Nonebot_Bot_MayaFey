"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/1 21:42
"""
import ujson as json
import nonebot

from typing import Dict
from utils import users
from fastapi import FastAPI, Body
from .utils import *
from utils.other import add_target

# 插件元数据定义
__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name="api",
    description="API",
    usage="被动, 无命令" + add_target(60),
    extra={
        "generate_type": "none",
        "author": "Shine_Light",
        "translate": "API",
    }
)

app: FastAPI = nonebot.get_app()


@app.post("/api/test")
async def connect_test():
    return 200


@app.post("/api/member/get_group_list")
async def get_group_list():
    try:
        bot = nonebot.get_bot()
        group_list: list = await bot.call_api("get_group_list")
        return {"code": 200, "num": len(group_list), "data": group_list}
    except Exception as e:
        return {"code": -1, "error": str(e)}


@app.post("/api/member/get_group_member_list")
async def get_group_member_list(data=Body(None)) -> Dict[str, int]:
    try:
        bot = nonebot.get_bot()
        if type(data) == bytes:
            data = json.loads(data.decode("gbk"))
        else:
            data = json.loads(data)
        gid = data["gid"]
        member_list: list = await bot.call_api("get_group_member_list", group_id=int(gid))
        for member in member_list:
            credit = users.get_credit(gid=gid, uid=member["user_id"])
            ban_count = users.get_ban_count(gid=gid, uid=member["user_id"])
            if credit == -1:
                credit = 0
            member.update({"credit": credit, "ban_count": ban_count})
        return {"code": 200, "num": len(member_list), "data": member_list}
    except Exception as e:
        return {"code": -1, "error": str(e)}


@app.post("/api/plugin/get_plugins_list")
async def get_plugins_list(data=Body(None)) -> Dict[str, int]:
    try:
        if type(data) == bytes:
            data = json.loads(data.decode("gbk"))
        else:
            data = json.loads(data)
        gid = str(data["gid"])
        plugins = await get_plugin_list()
        plugins_full_list = []
        for plugin in plugins:
            plugins_full_list.append(await get_plugin_detail(gid, plugin))
        return {"code": 200, "data": plugins_full_list}
    except FileNotFoundError:
        return {"code": -1, "error": "找不到配置文件,该群可能未进行初始化"}
    except Exception as e:
        return {"code": -1, "error": str(e)}
