"""
Author       : Lancercmd
Date         : 2020-12-14 13:29:38
LastEditors  : Lancercmd
LastEditTime : 2022-02-15 02:10:58
Description  : None
GitHub       : https://github.com/Lancercmd
"""
from binascii import b2a_base64
from copy import deepcopy
from hashlib import sha1
from hmac import new
from random import randint
from sys import maxsize, version_info
from time import time

from aiohttp import request
from loguru import logger
from nonebot import get_driver, on_command
from nonebot.adapters import Event, Message, MessageTemplate
from nonebot.adapters.onebot.v11 import MessageEvent as OneBot_V11_MessageEvent
from nonebot.exception import ActionFailed
from nonebot.params import CommandArg
from nonebot.permission import Permission
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from ujson import loads as loadJsonS
from ._permission import onFocus

from utils.other import add_target


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="translate_tencent",
    description="翻译(腾讯接口版本)",
    usage="/腾讯翻译" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "Lancercmd",
        "translate": "腾讯翻译",
    }
)

config = get_driver().config

translate = on_command("腾讯翻译", aliases={"腾讯机翻"}, priority=7)


@translate.permission_updater
async def _(event: Event) -> Permission:
    return await onFocus(event)


async def getReqSign(params: dict) -> str:
    common = {
        "Action": "TextTranslate",
        "Region": f"{getattr(config, 'tencentcloud_common_region', 'ap-shanghai')}",
        "Timestamp": int(time()),
        "Nonce": randint(1, maxsize),
        "SecretId": f"{getattr(config, 'tencentcloud_common_secretid', '')}",
        "Version": "2018-03-21",
    }
    params.update(common)
    sign_str = "POSTtmt.tencentcloudapi.com/?"
    sign_str += "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    secret_key = getattr(config, "tencentcloud_common_secretkey", "")
    if version_info[0] > 2:
        sign_str = bytes(sign_str, "utf-8")
        secret_key = bytes(secret_key, "utf-8")
    hashed = new(secret_key, sign_str, sha1)
    signature = b2a_base64(hashed.digest())[:-1]
    if version_info[0] > 2:
        signature = signature.decode()
    return signature


@translate.handle()
async def _(event: Event, state: T_State, args: Message = CommandArg()):
    if isinstance(event, OneBot_V11_MessageEvent):
        available = [
            # "auto",
            "zh", "zh-TW", "en", "ja", "ko", "fr",
            "es", "it", "de", "tr", "ru", "pt",
            "vi", "id", "th", "ms", "ar", "hi"
        ]
        state["available"] = " | ".join(available)
        state["valid"] = deepcopy(available)
        _plain_text = args.extract_plain_text()
        if _plain_text:
            for language in available:
                if _plain_text.startswith(language):
                    state["Source"] = language
                    break
                elif _plain_text.startswith("jp"):
                    state["Source"] = "ja"
                    break
            if "Source" in state:
                input = _plain_text.split(" ", 2)
                available.remove("zh-TW")
                if state["Source"] == "zh-TW":
                    available.remove("zh")
                if state["Source"] != "en":
                    for i in ["ar", "hi"]:
                        available.remove(i)
                if not state["Source"] in ["zh", "zh-TW", "en"]:
                    for i in ["vi", "id", "th", "ms"]:
                        available.remove(i)
                if state["Source"] in ["ja", "ko", "vi", "id", "th", "ms", "ar", "hi"]:
                    for i in ["fr", "es", "it", "de", "tr", "ru", "pt"]:
                        available.remove(i)
                if not state["Source"] in ["zh", "zh-TW", "en", "ja", "ko"]:
                    for i in ["ja", "ko"]:
                        available.remove(i)
                if state["Source"] in ["ar", "hi"]:
                    available.remove("zh")
                try:
                    available.remove(state["Source"])
                except ValueError:
                    pass
                if len(available) == 1:
                    state["Target"] = available[0]
                    if len(input) == 3:
                        state["SourceText"] = input[2]
                    else:
                        state["SourceText"] = input[1]
                elif len(input) == 3:
                    state["Target"] = input[1]
                    state["SourceText"] = input[2]
                elif len(input) == 2:
                    for language in available:
                        if input[0] in available:
                            state["Target"] = input[1]
                        else:
                            state["SourceText"] = input[1]
            else:
                state["SourceText"] = _plain_text
        message = f"请选择输入语种，可选值如下~\n{state['available']}"
        if "header" in state:
            message = "".join([state["header"], f"{message}"])
        state["prompt"] = message
    else:
        logger.warning("Not supported: translator")
        return


@translate.got("Source", prompt=MessageTemplate("{prompt}"))
async def _(event: Event, state: T_State):
    if isinstance(event, OneBot_V11_MessageEvent):
        _source = str(state["Source"])
        try:
            available = deepcopy(state["valid"])
            if _source.lower() == "jp":
                _source = "ja"
            elif not _source in state["valid"]:
                message = f"不支持的输入语种 {_source}"
                if "header" in state:
                    message = "".join([state["header"], f"{message}"])
                await translate.finish(message)
            available.remove("zh-TW")
            if _source == "zh-TW":
                available.remove("zh")
            if _source != "en":
                for i in ["ar", "hi"]:
                    available.remove(i)
            if not _source in ["zh", "zh-TW", "en"]:
                for i in ["vi", "id", "th", "ms"]:
                    available.remove(i)
            if _source in ["ja", "ko", "vi", "id", "th", "ms", "ar", "hi"]:
                for i in ["fr", "es", "it", "de", "tr", "ru", "pt"]:
                    available.remove(i)
            if not _source in ["zh", "zh-TW", "en", "ja", "ko"]:
                for i in ["ja", "ko"]:
                    available.remove(i)
            if _source in ["ar", "hi"]:
                available.remove("zh")
            try:
                available.remove(_source)
            except ValueError:
                pass
            if len(available) == 1:
                state["Target"] = available[0]
            else:
                state["available"] = " | ".join(available)
                state["valid"] = deepcopy(available)
            message = f"请选择目标语种，可选值如下~\n{state['available']}"
            if "header" in state:
                message = "".join([state["header"], f"{message}"])
            state["prompt"] = message
        except ActionFailed as e:
            logger.warning(
                f"ActionFailed {e.info['retcode']} {e.info['msg'].lower()} {e.info['wording']}"
            )
    else:
        logger.warning("Not supported: translator")
        return


@translate.got("Target", prompt=MessageTemplate("{prompt}"))
async def _(event: Event, state: T_State):
    if isinstance(event, OneBot_V11_MessageEvent):
        _target = str(state["Target"])
        try:
            if _target.lower() == "jp":
                _target = "ja"
            elif not _target in state["valid"]:
                message = f"不支持的目标语种 {_target}"
                if "header" in state:
                    message = "".join([state["header"], f"{message}"])
                await translate.finish(message)
            message = "请输入要翻译的内容~"
            if "header" in state:
                message = "".join([state["header"], f"{message}"])
            state["prompt"] = message
        except ActionFailed as e:
            logger.warning(
                f"ActionFailed {e.info['retcode']} {e.info['msg'].lower()} {e.info['wording']}"
            )
    else:
        logger.warning("Not supported: translator")
        return


@translate.got("SourceText", prompt=MessageTemplate("{prompt}"))
async def _(event: Event, state: T_State):
    if isinstance(event, OneBot_V11_MessageEvent):
        _source_text = str(state["SourceText"])
        _source = state["Source"]
        _target = state["Target"]
        try:
            endpoint = "https://tmt.tencentcloudapi.com"
            params = {
                "Source": _source,
                "SourceText": _source_text,
                "Target": _target,
                "ProjectId": 0,
            }
            params["Signature"] = await getReqSign(params)
            async with request("POST", endpoint, data=params) as resp:
                code = resp.status
                if code != 200:
                    message = "※ 网络异常，请稍后再试~"
                    if "header" in state:
                        message = "".join([state["header"], f"{message}"])
                    await translate.finish(message)
                data = loadJsonS(await resp.read())["Response"]
            if "Error" in data:
                message = "\n".join(
                    [
                        f"<{data['Error']['Code']}> {data['Error']['Message']}",
                        f"RequestId: {data['RequestId']}",
                    ]
                )
                if "header" in state:
                    message = "".join([state["header"], f"{message}"])
                await translate.finish(message)
            message = data["TargetText"]
            if "header" in state:
                message = "".join([state["header"], f"{message}"])
            await translate.finish(message)
        except ActionFailed as e:
            logger.warning(
                f"ActionFailed {e.info['retcode']} {e.info['msg'].lower()} {e.info['wording']}"
            )
    else:
        logger.warning("Not supported: translator")
