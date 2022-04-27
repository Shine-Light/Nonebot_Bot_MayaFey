import re

from nonebot import get_driver, on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.log import logger

from .config import Config
from .render_pic import render
from .weather_data import Weather, CityNotFoundError, ConfigError

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

weather = on_regex(r".*?(.*)天气.*?", priority=7)


def get_msg(msg) -> str:
    msg1 = re.search(r".*?(.*)天气.*?", msg)
    msg2 = re.search(r".*?天气(.*).*?", msg)
    msg1 = msg1.group(1).replace(" ", "")
    msg2 = msg2.group(1).replace(" ", "")
    msg = msg1 if msg1 else msg2

    return msg


@weather.handle()
async def _(bot: Bot, event: MessageEvent):
    city = get_msg(event.get_plaintext())
    if not city:
        await weather.finish("地点是...空气吗?? >_<")

    w_data = Weather(city_name=city, api_key=api_key, api_type=api_type)
    try:
        await w_data.load_data()
    except CityNotFoundError:
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
