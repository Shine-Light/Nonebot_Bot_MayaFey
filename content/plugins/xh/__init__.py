import requests
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event

from utils.other import add_target, translate
from nonebot.plugin import PluginMetadata


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "xh"),
    description="随机笑话",
    usage="/笑话" + add_target(60)
)


url = "https://api.vvhan.com/api/xh"
xh = on_command(cmd="随机笑话", aliases={"笑话"}, priority=8)
@xh.handle()
async def _(bot: Bot, event: Event):
    status = requests.get(url, allow_redirects=False).status_code
    if status == 200:
        await bot.send(
            event=event,
            message=requests.get(url).text
        )
    else:
        await bot.send(
            event=event,
            message=f"接口出错,状态码:{status}"
        )
