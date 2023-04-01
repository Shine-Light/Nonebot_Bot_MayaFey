import nonebot
from .config import Config
from .data_source import translate_msg, LANGUAGES
from typing import Tuple, Any
from nonebot.plugin import PluginMetadata
from nonebot import on_regex
from nonebot.params import RegexGroup
from utils.other import add_target

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="translate_baidu",
    description="翻译(百度接口版本)",
    usage=f"x翻x {{内容}}\n"
          f"x译x {{内容}}\n"
          f"其中x可以为: {', '.join(LANGUAGES.keys())}" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "NumberSir",
        "translate": "百度翻译",
    }
)


translate = on_regex(r"^(.*)?(翻|译)(.*?)\s(.*)?$", priority=12, block=False)
@translate.handle()
async def _(reg_group: Tuple[Any, ...] = RegexGroup()):
    _query = reg_group[-1].strip()  # 翻译内容
    _from, _to = reg_group[0], reg_group[2]
    if _from and _to:
        _from_to = [_from, _to]
    else:
        await translate.finish(f"指令打错啦！请输入“x翻x 内容” ”x译x 内容”\n其中x可以为: {', '.join(LANGUAGES.keys())}", at_sender=True)

    if len(_query) > 2000:
        await translate.finish("翻译过长！请不要超过2000字", at_sender=True)
    await translate.send(await translate_msg(_from_to, _query), at_sender=True)
