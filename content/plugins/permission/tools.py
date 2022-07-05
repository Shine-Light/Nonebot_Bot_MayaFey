"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/30 21:13
"""
from utils.path import *
from utils import json_tools


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
    if role == 'Van':
        return 6
    elif role == 'owner':
        return 5
    elif role == 'admin':
        return 4
    elif role == 'superuser':
        return 3
    elif role == 'member':
        return 2
    elif role == 'baned':
        return 1
    else:
        return -1


# 根据等级获取role
def get_role(lev: int) -> str:
    if lev == 6:
        return "Van"
    elif lev == 5:
        return "owner"
    elif lev == 4:
        return "admin"
    elif lev == 3:
        return "superuser"
    elif lev == 2:
        return "member"
    elif lev == 1:
        return "baned"
    else:
        return 'None'


# role中文
def role_cn(role: str) -> str:
    if role == '根用户':
        return "Van"
    elif role == 'owner':
        return "群主"
    elif role == 'admin':
        return "管理员"
    elif role == 'superuser':
        return "超级用户"
    elif role == 'member':
        return "成员"
    elif role == 'baned':
        return "黑名单"
    else:
        return role


# role英文
def role_en(role: str) -> str:
    if role == 'Van':
        return "根用户"
    elif role == '群主':
        return "owner"
    elif role == '管理员':
        return "admin"
    elif role == '超级用户':
        return "superuser"
    elif role == '成员':
        return "member"
    elif role == '黑名单':
        return "baned"
    else:
        return role


def special_per(role: str, name: str, gid: str) -> bool:
    special_path = permission_special_base / f"{gid}.json"
    specials: dict = json_tools.json_load(special_path)
    return permission_(role, specials[name])


def get_special_per(gid: str, name: str) -> str:
    special_path = permission_special_base / f"{gid}.json"
    specials: dict = json_tools.json_load(special_path)
    return specials[name]


def get_plugin_permission(gid: str, plugin: str):
    plugin_per_config = json_tools.json_load(permission_common_base / f"{gid}.json")
    try:
        return plugin_per_config[plugin]
    except KeyError:
        return "多种"
