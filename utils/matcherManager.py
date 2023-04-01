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
    Matcher����, ����Matcher�������
    """
    __matchers__: Dict[str, Matcher] = field(default_factory=dict)

    def addMatcher(self, name: str, matcher: Matcher):
        """
        ���Matcher
        name: ����Ȩ������
        matcher: Matcher����
        """
        matcher.__matcher_name__ = name
        self.__matchers__.update({name: matcher})

    def removeMatcherByName(self, name: str):
        """
        �Ƴ�Matcher
        name: ����Ȩ������
        """
        self.__matchers__.pop(name)

    def removeMatcherByMatcher(self, matcher: Matcher):
        """
        �Ƴ�Matcher
        matcher: Matcher����
        """
        for name, matcher_ in self.__matchers__.items():
            try:
                if matcher_.__matcher_name__ == matcher.__matcher_name__:
                    self.__matchers__.pop(name)
            except AttributeError:
                pass

    def isMatcherExist(self, matcher: Matcher):
        """
        ��� Matcher���� �Ƿ����
        matcher: Matcher����
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
        ��� ����Ȩ������ �Ƿ����
        name: ����Ȩ������
        """
        if name in self.__matchers__.keys():
            return True
        else:
            return False

    def getMatcher(self, name: str):
        """
        ���� ����Ȩ������ ��ȡ Matcher����
        name: ����Ȩ������
        """
        return self.__matchers__.get(name)

    def getName(self, matcher: Matcher):
        """
        ���� Matcher���� ��ȡ ����Ȩ������
        matcher: Matcher����
        """
        for name, matcher_ in self.__matchers__.items():
            try:
                if matcher_.__matcher_name__ == matcher.__matcher_name__:
                    return name
            except AttributeError:
                pass


matcherManager = MatcherManager()
