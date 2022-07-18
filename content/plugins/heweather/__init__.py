from typing import Tuple
from nonebot import get_driver, on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from .config import Config
from .render_pic import render
from .weather_data import Weather, CityNotFoundError, ConfigError

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "heweather"),
    description="查看近几天的天气",
    usage="{城市名}天气" + add_target(60)
)


plugin_config = Config.parse_obj(get_driver().config.dict())

if plugin_config.qweather_apikey and plugin_config.qweather_apitype:
    api_key = plugin_config.qweather_apikey
    api_type = int(plugin_config.qweather_apitype)
else:
    raise ConfigError("请设置 qweather_apikey 和 qweather_apitype")


if plugin_config.debug:
    DEBUG = True
    logger.debug("将会保存图片到 weather.png")
else:
    DEBUG = False

weather = on_regex(r".*?(.*)天气(.*).*?", priority=7)
@weather.handle()
async def _(matcher: Matcher, args: Tuple[str, ...] = RegexGroup()):
    city = args[0].strip() or args[1].strip()
    if not city:
        await weather.finish("地点是...空气吗?? >_<")

    w_data = Weather(city_name=city, api_key=api_key, api_type=api_type)
    try:
        await w_data.load_data()
    except CityNotFoundError:
        matcher.block = False
        await weather.finish()

    img = await render(w_data)

    if DEBUG:
        debug_save_img(img)

    await weather.finish(MessageSegment.image(img))


def debug_save_img(img: bytes) -> None:
    from io import BytesIO

    from PIL import Image

    logger.debug("保存图片到 weather.png")
    a = Image.open(BytesIO(img))
    a.save("weather.png", format="PNG")
