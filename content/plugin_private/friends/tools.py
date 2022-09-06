"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/9/3 17:43
"""
from utils.json_tools import json_write, json_load
from utils.path import friends_request_info


def getRequestList() -> dict:
    js = json_load(friends_request_info)
    return js


def getRequestDetail(uid) -> str:
    js = json_load(friends_request_info)
    js = js[str(uid)]
    msg = f"{uid} 的请求:\n" \
          f"验证信息: {js['comment']}\n" \
          f"时间: {js['time']}"
    return msg


def deleteRequest(uid):
    js = json_load(friends_request_info)
    js.pop(str(uid))
    json_write(friends_request_info, js)


def getRequestFlag(uid) -> str:
    js = json_load(friends_request_info)
    return js[uid]['flag']
