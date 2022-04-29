import requests
import json
import time

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent
from ..withdraw import add_target


def getHot(event: GroupMessageEvent) -> str:
    # 天行数据API,每天有数次限制
    url = "http://api.tianapi.com/networkhot/index"
    token = "2b366ec357c394cd75611cbdd498ca3a"
    r = requests.post(url + "?key=" + token)
    status = r.status_code
    if status != 200 and status != 301 and status != 302:
        return f"接口调用失败,错误码{status}"
    msg: dict = json.loads(r.text)
    status = str(msg.get("code"))
    ft: str = "%Y-%m-%d %H:%M:%S"

    if status != "200":
        if status == "150":
            error = "次数已达上限"
        elif status == "130":
            error = "频率过高"
        elif status == "100" or status == "110":
            error = "服务正在维护"
        else:
            error = "未知错误请联系管理员"
        return "调用出错,%s" % error

    newsList: list = msg.get("newslist")
    num: int = 0
    content: list = []
    hotnums: list = []
    localTime = time.strftime(ft, time.localtime())
    message: str = "全网热搜排名,当前时间:" + localTime + "\n事件:热度值"

    for i in range(10):
        content.append(dict.get(newsList[num], "title"))
        hotnums.append(dict.get(newsList[num], "hotnum"))
        num += 1

    for i in range(10):
        message += "\n%s:%d" % (content[i], hotnums[i])

    return message

    # 韩小韩接口,大陆IP使用
    # url = "https://api.vvhan.com/api/hotlist?type="
    # mode = str(event.get_message()).split(" ", 1)[1]
    # last = ""
    # message = ""
    #
    # if mode == "知乎":
    #     last = "zhihuHot"
    # elif mode in ["百度", "baidu"]:
    #     last = "baiduRD"
    # elif mode in ["B站", "bilibili", "b站", "BILIBILI", "BiliBili"]:
    #     last = "bili"
    # elif mode in ["历史今天", "历史上的今天"]:
    #     last = "history"
    # elif mode in ["贴吧", "贴吧热议"]:
    #     last = "baiduRY"
    # elif mode in ["微博", "weibo"]:
    #     last = "wbHot"
    # elif mode in ["科技", "IT", "it"]:
    #     last = "itInfo"
    # else:
    #     last = None
    #
    # if not last:
    #     return "参数不完整,请查看帮助"
    #
    # userAgent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                            "Chrome/100.0.4896.127 Safari/537.36"}
    # request = requests.get(url + last, headers=userAgent)
    # text = request.text
    # state = request.status_code
    #
    # if state not in [200, 301, 302]:
    #     return f"请求出错,状态码{state}"
    #
    # js = json.loads(text)
    #
    # if js['success']:
    #     message = js["title"]
    #     data: list = js['data']
    #     for i in range(10):
    #         message += f"\n{i + 1}.{data[i]['title']}"
    #     return message
    #
    # else:
    #     return "接口请求出错,请重试"


netHot = on_command(cmd="热搜", priority=8)


@netHot.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await netHot.send(
        message=getHot(event)
    )
