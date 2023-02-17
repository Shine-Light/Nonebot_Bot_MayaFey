"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/15 16:53
"""
from dataclasses import dataclass, field
from typing import Dict
from nonebot.matcher import Matcher
from nonebot.log import logger
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

@dataclass
class MatcherPermissions(object):
    """
    Matcher权限控制
    """
    __matcherPers__: Dict[str, Matcher] = field(default_factory=dict)

    def addMatcher(self, name: str, matcher: Matcher):
        """
        添加Matcher权限控制
        name: 特殊权限名称
        matcher: Matcher对象
        """
        matcher.__matcher_name__ = name
        self.__matcherPers__.update({name: matcher})

    def removeMatcherByName(self, name: str):
        """
        移除Matcher权限控制
        name: 特殊权限名称
        """
        self.__matcherPers__.pop(name)

    def removeMatcherByMatcher(self, matcher: Matcher):
        """
        移除Matcher权限控制
        matcher: Matcher对象
        """
        for name in self.__matcherPers__.keys():
            try:
                if self.__matcherPers__.get(name).__matcher_name__ == matcher.__matcher_name__:
                    self.__matcherPers__.pop(name)
            except AttributeError:
                pass

    def isMatcherExist(self, matcher: Matcher):
        """
        检测 Matcher对象 是否添加权限控制
        matcher: Matcher对象
        """
        for name in self.__matcherPers__.keys():
            try:
                if self.__matcherPers__.get(name).__matcher_name__ == matcher.__matcher_name__:
                    return True
            except AttributeError:
                pass
        return False

    def isNameExist(self, name: str):
        """
        检测 特殊权限名称 是否添加权限控制
        name: 特殊权限名称
        """
        if name in self.__matcherPers__.keys():
            return True
        else:
            return False

    def getMatcher(self, name: str):
        """
        根据 特殊权限名称 获取 Matcher对象
        name: 特殊权限名称
        """
        return self.__matcherPers__.get(name)

    def getName(self, matcher: Matcher):
        """
        根据 Matcher对象 获取 特殊权限名称
        matcher: Matcher对象
        """
        for name in self.__matcherPers__.keys():
            try:
                if self.__matcherPers__.get(name).__matcher_name__ == matcher.__matcher_name__:
                    return name
            except AttributeError:
                pass


matcherPers = MatcherPermissions()
