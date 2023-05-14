import psutil
import datetime

from fastapi import Depends, FastAPI, Body
from nonebot import get_app, get_driver
from ..model import Result
from ..utils import auth


driver = get_driver()
app: FastAPI = get_app()
runtime_start = datetime.datetime.now()

@driver.on_startup
async def _():
    global runtime_start
    runtime_start = datetime.datetime.now()


@app.post("/api/system/usage", response_model=Result, dependencies=[Depends(auth)])
async def plugin_enable() -> Result:
    return Result(0, data={
        "cpu": psutil.cpu_percent(0.5),
        "memory": psutil.virtual_memory(),
        "disk": psutil.disk_usage("/"),
        "runtime": datetime.datetime.now() - runtime_start
    })
