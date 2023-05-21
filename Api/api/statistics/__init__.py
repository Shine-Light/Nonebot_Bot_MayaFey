import datetime
import aiofiles

from fastapi import Depends, FastAPI, Body
from nonebot import get_app
from ..model import Result, Group, Data
from ..utils import auth
from utils import path, json_tools, const


app: FastAPI = get_app()

async def remove_total_unable(plugins: dict):
    async with aiofiles.open(path.total_unable) as file:
        total_unable = (await file.read()).split(",")
        for plugin in list(plugins.keys()):
            if plugin in total_unable:
                plugins.pop(plugin)

@app.post("/api/statistics/plugins_call_total_monthly", response_model=Result, dependencies=[Depends(auth)])
async def plugin_call_total_monthly(group: Group, data: Data) -> Result:
    if not data.month:
        data.month = datetime.datetime.now().strftime(const.DATE_MONTH_FORMAT_STR)
    total_month = await json_tools.json_load_async(path.total_base / data.month / f"{group.group_id}.json")
    await remove_total_unable(total_month)
    return Result(0,data=total_month)


@app.post("/api/statistics/plugins_call_total", response_model=Result, dependencies=[Depends(auth)])
async def plugin_call_total(group: Group) -> Result:
    data = {}
    for monthly in path.total_base.glob("*"):
        if monthly.is_dir():
            try:
                total_month = await json_tools.json_load_async(monthly / f"{group.group_id}.json")
            except FileNotFoundError:
                continue
            await remove_total_unable(total_month)
            for plugin, count in total_month.items():
                if plugin in data:
                    data.update({plugin: data[plugin] + count})
                else:
                    data.update({plugin: count})
        else:
            continue
    return Result(0,data=data)


@app.post("/api/statistics/plugins_permission_count", response_model=Result, dependencies=[Depends(auth)])
async def plugins_permission_count(group: Group) -> Result:
    data = {}
    for per in (await json_tools.json_load_async(path.permission_common_base / f"{group.group_id}.json")).values():
        if per in data:
            data.update({per: data[per] + 1})
        else:
            data.update({per: 1})
    for per in (await json_tools.json_load_async(path.permission_special_base / f"{group.group_id}.json")).values():
        if per in data:
            data.update({per: data[per] + 1})
        else:
            data.update({per: 1})
    return Result(0,data=data)


@app.post("/api/statistics/plugins_permission_count_without_special", response_model=Result, dependencies=[Depends(auth)])
async def plugins_permission_count_without_special(group: Group) -> Result:
    try:
        data = {}
        for per in (await json_tools.json_load_async(path.permission_common_base / f"{group.group_id}.json")).values():
            if per in data:
                data.update({per: data[per] + 1})
            else:
                data.update({per: 1})
        return Result(0,data=data)
    except FileNotFoundError:
        return Result(0)