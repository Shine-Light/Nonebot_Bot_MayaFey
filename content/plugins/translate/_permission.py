"""
Author       : Lancercmd
Date         : 2021-03-12 16:21:29
LastEditors  : Lancercmd
LastEditTime : 2022-01-08 17:28:09
Description  : None
GitHub       : https://github.com/Lancercmd
"""
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.permission import Permission


async def onFocus(event: Event) -> Permission:
    """
    说明

      * 专注于当前会话类型，需配合 `nonebot.matcher.Matcher.permission_updater` 使用

    示例

      * 见连续会话实例
    """
    message_type = event.message_type
    user_id = event.get_user_id()
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id

    async def _onFocus(event: Event):
        if isinstance(event, GroupMessageEvent):
            return (
                event.message_type == message_type
                and event.get_user_id() == user_id
                and event.group_id == group_id
            )
        elif isinstance(event, PrivateMessageEvent):
            return event.message_type == message_type and event.get_user_id() == user_id

    return Permission(_onFocus)
