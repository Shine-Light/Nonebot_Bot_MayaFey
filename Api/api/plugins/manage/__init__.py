import aiofiles

from fastapi import Depends, FastAPI, Body
from nonebot import get_app
from ...model import Result, Group, Plugin
from ...exception import ParamError
from ...utils import auth
from utils import path, json_tools, config
from utils.permission import get_plugin_spcial_permissions


app: FastAPI = get_app()


@app.post("/api/plugins/manage/plugin_enable", response_model=Result, dependencies=[Depends(auth)])
async def plugin_enable(group: Group, plugin: Plugin) -> Result:
    plugin_name = plugin.plugin_name
    if plugin_name not in config.manager.pluginConfigs():
        return Result(102, "插件配置不存在!")
    await json_tools.json_update_async(path.control_path / group.group_id / "control.json", plugin_name, True)
    return Result(0)


@app.post("/api/plugins/manage/plugin_disable", response_model=Result, dependencies=[Depends(auth)])
async def plugin_disable(group: Group, plugin: Plugin) -> Result:
    plugin_name = plugin.plugin_name
    if plugin_name not in config.manager.pluginConfigs():
        return Result(102, "插件配置不存在!")
    await json_tools.json_update_async(path.control_path / group.group_id / "control.json", plugin_name, False)
    return Result(0)


@app.post("/api/plugins/manage/plugin_total_enable", response_model=Result, dependencies=[Depends(auth)])
async def plugin_total_enable(group: Group, plugin: Plugin) -> Result:
    plugin_name = plugin.plugin_name
    async with aiofiles.open(path.total_unable, "r", encoding="utf-8") as file:
        if plugin_name in (await file.read()).split(","):
            return Result(0)
    async with aiofiles.open(path.total_unable, "a", encoding="utf-8") as file:
        await file.write(f",{plugin_name}")
        return Result(0)


@app.post("/api/plugins/manage/plugin_total_disable", response_model=Result, dependencies=[Depends(auth)])
async def plugin_total_disable(group: Group, plugin: Plugin) -> Result:
    plugin_name = plugin.plugin_name
    configs = []
    async with aiofiles.open(path.total_unable, "r+", encoding="utf-8") as file:
        configs = (await file.read()).split(",")
        if plugin_name in set(configs):
            configs.remove(plugin_name)
        else:
            return Result(0)
    async with aiofiles.open(path.total_unable, "w+", encoding="utf-8") as file:
        await file.write(",".join(configs))
        return Result(0)


@app.post("/api/plugins/manage/plugin_permission_update", response_model=Result, dependencies=[Depends(auth)])
async def plugin_permission_update(group: Group, plugin: Plugin) -> Result:
    if not plugin.permission:
        raise ParamError
    plugin_name = plugin.plugin_name
    permission: dict = plugin.permission
    permission_common_path = path.permission_common_base / f"{group.group_id}.json"
    permission_special_path = path.permission_special_base / f"{group.group_id}.json"
    if not plugin_name in config.manager.pluginConfigs():
        return Result(102, "插件配置不存在!")  
    if permission.get("permission_common"):
        await json_tools.json_update_async(permission_common_path, plugin_name, permission.get("permission_common"))
    if permission.get("permission_special"):
        for matcher_name, per in permission.get("permission_special").items():
            await json_tools.json_update_async(permission_special_path, matcher_name, per)
    for matcher_name in get_plugin_spcial_permissions(group.group_id, plugin.plugin_name):
        if matcher_name not in permission.get("permission_special"):
            await json_tools.json_pop_async(permission_special_path, matcher_name)
    return Result(0)


@app.post("/api/plugins/manage/plugin_cd_update", response_model=Result, dependencies=[Depends(auth)])
async def plugin_cd_update(group: Group, plugin: Plugin) -> Result:
    if not plugin.cd:
        raise ParamError
    plugin_name = plugin.plugin_name
    cd: dict = plugin.cd
    if not plugin_name in config.manager.pluginConfigs():
        return Result(102, "插件配置不存在!")  
    if cd.get("plugin"):
        cd_source = await json_tools.json_load_async(path.cd_path / group.group_id / "cd.json")
        cd_source.get(plugin_name).update({"plugin": cd.get("plugin")})
        await json_tools.json_write_async(path.cd_path / group.group_id / "cd.json", cd_source)
    if cd.get("matcher"):
        cd_source = await json_tools.json_load_async(path.cd_path / group.group_id / "cd.json")
        cd_source.get(plugin_name).update({"matcher": cd.get("matcher")})
        await json_tools.json_write_async(path.cd_path / group.group_id / "cd.json", cd_source)
    return Result(0)