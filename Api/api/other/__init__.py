from fastapi import Depends, FastAPI, Body
from nonebot import get_app
from ..model import Result
from ..utils import auth
from utils import path, json_tools, permission
from content.plugins.update.tools import update, get_version, get_version_last, check_update


app: FastAPI = get_app()


@app.post("/api/other/check_bot_update", response_model=Result, dependencies=[Depends(auth)])
async def check_bot_update() -> Result:
    return Result(0, data={
        "lastest": await get_version_last(),
        "current": get_version(),
        "update": await check_update(),
    })


@app.post("/api/other/update_bot", response_model=Result, dependencies=[Depends(auth)])
async def update_bot() -> Result:
    if await check_update():
        await update("", "api")
        return Result(0)
    else:
        return Result(102, "已是最新版本")


@app.post("/api/other/update_bot_respond", response_model=Result, dependencies=[Depends(auth)])
async def update_bot_respond() -> Result:
    status = await json_tools.json_load_async(path.updating_path)
    await json_tools.json_write_async(path.updating_path, {"updating": False, "error": "", "target": {"target": "", "target_type": ""}})
    if status.get("error"):
        return Result(101, msg=f"更新失败: {status['error']}")
    else:
        return Result(0)


@app.post("/api/other/get_availabel_permission", response_model=Result, dependencies=[Depends(auth)])
async def get_availabel_permission() -> Result:
    return Result(0, data=permission.permissions)
