"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/16 12:41
"""
import ujson as json

import requests

from nonebot import get_driver
from nonebot.log import logger


config = get_driver().config
api_type = config.ai_talk_api_type
tianx_error_code = {
    100: "内部服务器错误",
    110: "当前API已下线",
    120: "API暂时维护中",
    130: "API调用频率超限",
    140: "API没有调用权限",
    150: "API可用次数不足",
    160: "账号未申请该API",
    170: "Referer请求来源受限",
    180: "IP请求来源受限",
    190: "当前key已限制使用",
    230: "key错误或为空",
    240: "缺少key参数",
    250: "数据返回为空，请检查输入值或注意中文编码问题",
    260: "参数值不得为空",
    270: "参数值不符合要求",
    280: "缺少必要的参数",
    290: "超过最大输入字节限制"
}
moli_error_code = {
    "C1001": "当日调用次数已用完"
}


def get_tianx_config() -> dict:
    key = config.ai_talk_tianx_key
    mode = config.ai_talk_tianx_mode
    priv = config.ai_talk_tianx_priv
    return {"key": key, "mode": mode, "priv": priv}


def get_moli_config() -> dict:
    key = config.ai_talk_moli_key
    secret = config.ai_talk_moli_secret
    return {"key": key, "secret": secret}


def get_api_url(msg: str, uid: str, nickname: str, gid: str = "12345678") -> dict:
    if api_type == "qingyunke":
        return {"method": "GET", "url": f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"}
    elif api_type == "tianx":
        user_hash = hash(uid)
        restype = 0
        tianx_config = get_tianx_config()
        return {"method": "GET", "url":
            f"http://api.tianapi.com/robot/index?key={tianx_config['key']}"
            f"&question={msg}&mode={tianx_config['mode']}&uniqueid={user_hash}"
            f"&priv={tianx_config['priv']}&restype={restype}"
                }
    elif api_type == "moli":
        moli_config = get_moli_config()
        key = moli_config["key"]
        secret = moli_config["secret"]
        content = msg
        if gid == "12346578":
            chat_type = 1
        else:
            chat_type = 2
        chat_from = uid
        fromName = nickname
        to = gid
        args = {
            "content": content,
            "type": chat_type,
            "from": chat_from,
            "fromName": fromName,
            "to": to
        }
        headers = {"Api-Key": key, "Api-Secret": secret, "Content-Type": "application/json;charset=UTF-8"}
        return {"method": "POST", "url": "https://api.mlyai.com/reply", "args": args, "headers": headers}
    else:
        return None


def request_url(api_url: dict) -> dict:
    method = api_url["method"]
    url = api_url["url"]
    try:
        headers = api_url["headers"]
    except:
        headers = None
    if method == "GET":
        return requests.get(url, verify=False, headers=headers).json()
    else:
        args = api_url["args"]
        return requests.post(url, json.dumps(args), verify=False, headers=headers).json()


def error_parse(code: int) -> str:
    try:
        return tianx_error_code[code]
    except:
        return "未知错误"


def parse_res(data: dict) -> dict:
    if api_type == "qingyunke":
        if data["result"] == 0:
            return {
                "type": "other",
                "values": [
                    {"type": "text",
                     "value": data["content"]
                     }
                ]
            }
        else:
            logger.error(f"青云客API错误,状态码:{data['result']}")
    elif api_type == "tianx":
        if data["code"] == 200:
            values = []
            for value in data["newslist"]:
                values.append(
                    {
                        "type": value.pop("datatype"),
                        "value": value.pop("reply")
                    }
                )
            return {
                "type": "other",
                "values": values
            }
        else:
            logger.warning(f"天行API错误,{error_parse(data['code'])}")
    elif api_type == "moli":
        moli_content_url = "https://files.molicloud.com/"
        if data["code"] == "00000":
            values = []
            for value in data["data"]:
                typed = value["typed"]
                content = value["content"]
                if typed == 1 or typed == 8:
                    typed = "text"
                elif typed == 2:
                    typed = "image"
                    content = moli_content_url + content
                elif typed == 3:
                    typed = "docs"
                    content = moli_content_url + content
                elif typed == 4:
                    typed = "record"
                    content = moli_content_url + content
                elif typed == 9:
                    typed = "other"
                    content = moli_content_url + content
                values.append(
                    {
                        "type": typed,
                        "value": content
                    }
                )
            return {
                "type": "other",
                "values": values
            }
        else:
            logger.warning(f"茉莉云API错误, {data['message']}")
