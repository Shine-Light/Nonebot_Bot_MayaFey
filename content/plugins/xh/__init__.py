import requests
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event

url = "https://api.vvhan.com/api/xh"
menu = on_command(cmd="随机笑话", aliases={"笑话"}, priority=8)
@menu.handle()
async def menu1(bot: Bot, event: Event):
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
