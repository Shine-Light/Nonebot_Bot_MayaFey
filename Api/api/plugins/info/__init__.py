import aiofiles

from fastapi import Depends, FastAPI, Body
from nonebot import get_app
from ...model import Result, Group, Plugin
from ...utils import auth
from utils import permission, config, path, json_tools


app: FastAPI = get_app()


async def get_cd(plugin: str, gid: str):
    return (await json_tools.json_load_async(path.cd_path / gid / "cd.json")).get(plugin)

async def get_unset(plugin: str):
    async with aiofiles.open(path.unset_path, "r", encoding="utf-8") as file:
        return plugin in (await file.read()).split(",")

async def get_total_unable(plugin: str):
    async with aiofiles.open(path.total_unable, "r", encoding="utf-8") as file:
        return plugin in (await file.read()).split(",")


async def get_enable(plugin: str, gid: str):
    return (await json_tools.json_load_async(path.control_path / gid / "control.json")).get(plugin)


@app.post("/api/plugins/info/plugin_list", response_model=Result, dependencies=[Depends(auth)])
async def plugin_list(group: Group) -> Result:
    try:
        plugin_configs = config.manager.pluginConfigs()
        data = []
        for plugin_name, plugin_config in plugin_configs.items():
            plugin_data = {
                "plugin_name": plugin_name,
                **plugin_config.dict(),
                "permission_common": permission.get_plugin_permission(group.group_id, plugin_name),
                "permission_special": permission.get_plugin_spcial_permissions(group.group_id, plugin_name),
                "cd": await get_cd(plugin_name, group.group_id),
                "unset": await get_unset(plugin_name),
                "total_unable": await get_unset(plugin_name),
                "enable": await get_enable(plugin_name, group.group_id)
            }
            plugin_data.pop("plugin_meta")
            plugin_data.pop("usage")
            data.append(plugin_data)
        return Result(0, data={"plugin_list": data})
    except KeyError:
        return Result(102, "插件不存在或未加载!")


@app.post("/api/plugins/info/plugin_info", response_model=Result, dependencies=[Depends(auth)])
async def plugin_info(group: Group, plugin: Plugin) -> Result:
    try:
        plugin_configs = config.manager.pluginConfigs()

        plugin_name = plugin.plugin_name
        data = {
            "plugin_name": plugin_name,
            **plugin_configs[plugin_name].dict(),
            "permission_common": permission.get_plugin_permission(group.group_id, plugin_name),
            "permission_special": permission.get_plugin_spcial_permissions(group.group_id, plugin_name),
            "cd": await get_cd(plugin_name, group.group_id),
            "unset": await get_unset(plugin_name),
            "total_unable": await get_unset(plugin_name),
            "enable": await get_enable(plugin_name, group.group_id)
        }
        data.pop("plugin_meta")
        data.pop("usage")
        return Result(0, data=data)
    except KeyError:
        return Result(102, "插件不存在或未加载!")

@app.post("/api/plugins/info/get_plugins_translate", response_model=Result, dependencies=[Depends(auth)])
async def get_plugins_translate() -> Result:
    return Result(0, data=await json_tools.json_load_async(path.translate_path))

@app.post("/api/plugins/info/get_plugin_translate", response_model=Result, dependencies=[Depends(auth)])
async def get_plugin_translate(plugin: Plugin) -> Result:
    return Result(0, data={"translate": (await json_tools.json_load_async(path.translate_path))[plugin.plugin_name]})
