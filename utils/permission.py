"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/15 16:53
"""
from nonebot.log import logger
from utils.path import permissions_path, permission_special_base, permission_common_base
from utils import json_tools

try:
    permissions = json_tools.json_load(permissions_path)
except FileNotFoundError:
    logger.warning("找不到权限配置文件,只有默认配置")
    permissions = {
      "Van": {"name": "根用户", "level": 999},
      "owner": {"name": "群主", "level": 80},
      "admin": {"name": "管理员", "level": 60},
      "superuser": {"name": "超级用户", "level": 40},
      "member": {"name": "成员", "level": 20},
      "baned": {"name": "黑名单", "level": 0}
    }


def permission_(role: str, role_: str) -> bool:
    """
    权限等级检测,大于或等于
    role 待检测的权限
    role_ 目标权限
    """
    lev = get_lev(role)
    lev_ = get_lev(role_)
    return lev >= lev_


# 根据role获取等级
def get_lev(role: str) -> int:
    if permissions.get(role) and permissions.get(role).get("level") is not None:
        return permissions.get(role).get("level")
    else:
        logger.error(f"无法获取权限 {role},请检查权限配置")
        return -1


# role中文
def role_cn(role: str) -> str:
    if permissions.get(role) and permissions.get(role).get("name"):
        return permissions.get(role).get("name")
    else:
        return role


# role英文
def role_en(name: str) -> str:
    for p in permissions:
        if permissions.get(p).get("name") == name:
            return p
    else:
        return name


def have_special_per(matcher_name: str, gid: str) -> bool:
    """
    检测Matcher是否存在特殊权限
    matcher_name: matcher名称
    gid: 群号
    """
    special_path = permission_special_base / f"{gid}.json"
    specials: dict = json_tools.json_load(special_path)
    return matcher_name in specials


def special_per(role: str, name: str, gid: str) -> bool:
    """
    检测权限是否符合特殊权限
    role: 待检测权限
    name: 目标特殊权限名称
    gid: 群号
    """
    special_path = permission_special_base / f"{gid}.json"
    specials: dict = json_tools.json_load(special_path)
    try:
        return permission_(role, specials[name])
    except KeyError:
        logger.error(f"找不到特殊权限: {name}, 跳过权限检测")
        return True


def get_special_per(gid: str, name: str) -> str:
    """
    获取特殊权限
    name: 特殊权限名称
    gid: 群号
    """
    try:
        special_path = permission_special_base / f"{gid}.json"
        specials: dict = json_tools.json_load(special_path)
        return specials[name]
    except:
        return ""


def get_plugin_permission(gid: str, plugin: str):
    """
    获取插件普通权限
    gid: 群号
    plugin: 插件名
    """
    plugin_per_config = json_tools.json_load(permission_common_base / f"{gid}.json")
    try:
        return plugin_per_config[plugin]
    except KeyError:
        return None
