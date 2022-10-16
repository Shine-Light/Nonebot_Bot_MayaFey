"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:04
"""
import requests
from nonebot.exception import IgnoredException
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from utils import requests_tools

from utils.other import add_target, translate
from nonebot.plugin import PluginMetadata


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "ian"),
    description="一句鸡汤或者毒鸡汤",
    usage="/一言" + add_target(60)
)


url_api = 'https://tenapi.cn/yiyan/?format=text'

ian = on_command(cmd='一言', aliases={'一句一言', 'ian'}, priority=8)
@ian.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        proxy = requests_tools.get_proxy()
        if proxy:
            request = requests.get(url_api, proxies=proxy)
        else:
            request = requests.get(url_api)
        state = request.status_code

        if state not in [200]:
            await ian.finish(f"请求出错,状态码:{state}")

        await ian.send(request.text)
    except IgnoredException:
        return
    except Exception as e:
        await ian.send(str(e))
