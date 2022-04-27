"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:04
"""
import requests
from nonebot.exception import IgnoredException
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent

url_api = 'https://tenapi.cn/yiyan/?format=text'

ian = on_command(cmd='一言', aliases={'一句一言', 'ian'}, priority=8)
@ian.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        request = requests.get(url_api)
        state = request.status_code

        if state not in [200]:
            await ian.finish(f"请求出错,状态码:{state}")

        await ian.send(request.text)
    except IgnoredException:
        return
    except Exception as e:
        await ian.send(str(e))
