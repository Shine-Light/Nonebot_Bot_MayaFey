import hashlib

import httpx
from nonebot import get_driver

from .config import Config
from .utils import EXCEPTIONS, LANGUAGES
from nonebot import logger

baidu_config = Config.parse_obj(get_driver().config.dict())


async def translate_msg(_from_to, _query):
    lang = parse_language(_from_to)
    if lang is None:
        return f"指令打错啦！请输入“x翻x 内容”\n其中x可以为: {', '.join(LANGUAGES.keys())}"

    [_from, _to] = lang
    _appid = baidu_config.appid
    _salt = baidu_config.salt
    _key = baidu_config.key
    _sign = f"{_appid}{_query}{_salt}{_key}"
    _sign = hashlib.md5(bytes(_sign, 'utf-8')).hexdigest()

    async with httpx.AsyncClient() as client:
        success = False
        for times in range(5):
            try:
                url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
                params = {
                    "q": _query,
                    "from": _from,
                    "to": _to,
                    "appid": _appid,
                    "salt": _salt,
                    "sign": _sign,
                }

                json_data = await client.post(url, params=params)
            except Exception as e:
                logger.warning(f"第{times+1}次连接失败... {type(e)}: {e}")
                continue
            else:
                success = True
                break
    if not success:
        return f"QAQ，连接失败了...请重试..."

    json_data = json_data.json()
    logger.debug(f"结果: {json_data}")
    if "error_code" not in json_data.keys():
        _result = json_data['trans_result'][0]
        return f"\n原文：{_query}\n译文：{_result['dst']}"

    if json_data['error_code'] != "52000":
        raise EXCEPTIONS[json_data['error_code']]


def parse_language(_from_to):
    if len(_from_to) != 2:
        return None
    _rst = ["", ""]
    for idx, val in enumerate(_from_to):
        try:
            _rst[idx] = LANGUAGES[val]
        except KeyError:
            continue
    return _rst
