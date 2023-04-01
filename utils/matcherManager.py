"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/4/1 17:47
"""
from dataclasses import dataclass, field
from typing import Dict
from nonebot.matcher import Matcher

@dataclass
class MatcherManager(object):
    """
    Matcher管理, 用于Matcher级别控制
    """
    __matchers__: Dict[str, Matcher] = field(default_factory=dict)

    def addMatcher(self, name: str, matcher: Matcher):
        """
        添加Matcher
        name: 特殊权限名称
        matcher: Matcher对象
        """
        matcher.__matcher_name__ = name
        self.__matchers__.update({name: matcher})

    def removeMatcherByName(self, name: str):
        """
        移除Matcher
        name: 特殊权限名称
        """
        self.__matchers__.pop(name)

    def removeMatcherByMatcher(self, matcher: Matcher):
        """
        移除Matcher
        matcher: Matcher对象
        """
        for name, matcher_ in self.__matchers__.items():
            try:
                if matcher_.__matcher_name__ == matcher.__matcher_name__:
                    self.__matchers__.pop(name)
            except AttributeError:
                pass

    def isMatcherExist(self, matcher: Matcher):
        """
        检测 Matcher对象 是否存在
        matcher: Matcher对象
        """
        for name, matcher_ in self.__matchers__.items():
            try:
                if matcher_.__matcher_name__ == matcher.__matcher_name__:
                    return True
            except AttributeError:
                pass
        return False

    def isNameExist(self, name: str):
        """
        检测 特殊权限名称 是否存在
        name: 特殊权限名称
        """
        if name in self.__matchers__.keys():
            return True
        else:
            return False

    def getMatcher(self, name: str):
        """
        根据 特殊权限名称 获取 Matcher对象
        name: 特殊权限名称
        """
        return self.__matchers__.get(name)

    def getName(self, matcher: Matcher):
        """
        根据 Matcher对象 获取 特殊权限名称
        matcher: Matcher对象
        """
        for name, matcher_ in self.__matchers__.items():
            try:
                if matcher_.__matcher_name__ == matcher.__matcher_name__:
                    return name
            except AttributeError:
                pass


matcherManager = MatcherManager()
