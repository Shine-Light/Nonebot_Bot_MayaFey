"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/16 12:41
"""
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
turing_error_code = {
    5000: "无解析结果",
    6000: "暂不支持该功能",
    4000: "请求参数格式错误",
    4001: "加密方式错误",
    4002: "无功能权限",
    4003: "该apikey没有可用请求次数",
    4005: "无功能权限",
    4007: "apikey不合法",
    4100: "userid获取失败",
    4200: "上传格式错误",
    4300: "批量操作超过限制",
    4400: "没有上传合法userid",
    4500: "userid申请个数超过限制",
    4600: "输入内容为空",
    4602: "输入文本内容超长(上限150)",
    7002: "上传信息失败",
    8008: "服务器错误"
}


def get_tianx_config() -> dict:
    key = config.ai_talk_tianx_key
    mode = config.ai_talk_tianx_mode
    priv = config.ai_talk_tianx_priv
    return {"key": key, "mode": mode, "priv": priv}


def get_turing_config() -> dict:
    key = config.ai_talk_turing_key
    return {"key": key}


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
    elif api_type == "turing":
        turing_config = get_turing_config()
        restype = 0
        perception = {"inputText": msg}
        user_hash = hash(uid)
        user_info = {"apiKey": turing_config["key"], "userId": user_hash,
                     "groupId": gid, "userIdName": nickname}
        args = {"reqType": restype, "perception": perception, "userInfo": user_info}
        return {"method": "POST", "url": "http://openapi.turingapi.com/openapi/api/v2", "args": args}
    else:
        return None


def request_url(api_url: dict) -> dict:
    method = api_url["method"]
    url = api_url["url"]
    if method == "GET":
        return requests.get(url, verify=False).json()
    else:
        args = api_url["args"]
        return requests.post(url, args, verify=False).json()


def error_parse(code: int) -> str:
    if api_type == "tianx":
        try:
            return tianx_error_code[code]
        except:
            return "未知错误"
    elif api_type == "turing":
        try:
            return turing_error_code[code]
        except:
            return "未知错误"


def parse_res(data: dict) -> dict:
    if api_type == "qingyunke":
        if data["result"] == 0:
            return {"type": "text", "values": data["content"]}
        else:
            logger.error(f"青云客API错误,状态码:{data['result']}")
    elif api_type == "tianx":
        if data["code"] == 200:
            return {
                "type": data["newslist"][0]["datatype"],
                "values": data["newslist"][0]["reply"]
            }
        else:
            logger.warning(f"天行API错误,{error_parse(data['code'])}")
    elif api_type == "turing":
        if data["intent"]["code"] == 10005:
            return {
                "type": "turing",
                "values": data["results"]
            }
        else:
            logger.warning(f"图灵API错误,{error_parse(data['code'])}")
