"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/15 16:53
"""
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.permission import Permission
from .users import is_superuser_with_gid, is_Van


async def superuser_checker(event: GroupMessageEvent) -> bool:
    return is_superuser_with_gid(str(event.user_id), str(event.group_id))


async def Van_checker(event: GroupMessageEvent) -> bool:
    return is_Van(str(event.user_id))

superuser: Permission = Permission(superuser_checker)
Van: Permission = Permission(Van_checker)
