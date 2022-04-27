import base64
import jinja2
import imageio
import traceback
from io import BytesIO
from pathlib import Path
from typing import List, Union

from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page, html_to_pic


dir_path = Path(__file__).parent
template_path = dir_path / 'templates'
path_url = f"file://{template_path.absolute()}"
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def create_image(html: str):
    return await html_to_pic(html, viewport={"width": 100, "height": 100},
                             template_path=path_url)


async def create_pornhub_logo(left_text, right_text) -> bytes:
    template = env.get_template('pornhub.html')
    html = await template.render_async(left_text=left_text, right_text=right_text)
    return await create_image(html)


async def create_youtube_logo(left_text, right_text) -> bytes:
    template = env.get_template('youtube.html')
    html = await template.render_async(left_text=left_text, right_text=right_text)
    return await create_image(html)


async def create_5000choyen_logo(top_text, bottom_text) -> str:
    template = env.get_template('5000choyen.html')
    html = await template.render_async(top_text=top_text, bottom_text=bottom_text)

    async with get_new_page() as page:
        await page.goto(path_url)
        await page.set_content(html)
        await page.wait_for_selector('a')
        a = await page.query_selector('a')
        img = await (await a.get_property('href')).json_value()
    return 'base64://' + str(img).replace('data:image/png;base64,', '')


async def create_douyin_logo(text) -> BytesIO:
    template = env.get_template('douyin.html')
    html = await template.render_async(text=text, frame_num=10)

    async with get_new_page() as page:
        await page.goto(path_url)
        await page.set_content(html)
        imgs = await page.query_selector_all('a')
        imgs = [await (await img.get_property('href')).json_value() for img in imgs]

    imgs = [imageio.imread(base64.b64decode(
        str(img).replace('data:image/png;base64,', ''))) for img in imgs]

    output = BytesIO()
    imageio.mimsave(output, imgs, format='gif', duration=0.2)
    return output


async def create_google_logo(text) -> BytesIO:
    template = env.get_template('google.html')
    html = await template.render_async(text=text)
    return await create_image(html)


commands = {
    'pornhub': {
        'aliases': {'ph ', 'phlogo', 'P站logo'},
        'func': create_pornhub_logo,
        'arg_num': 2
    },
    'youtube': {
        'aliases': {'yt ', 'ytlogo', '油管logo'},
        'func': create_youtube_logo,
        'arg_num': 2
    },
    '5000choyen': {
        'aliases': {'5000兆', '5000choyen', '五千兆logo'},
        'func': create_5000choyen_logo,
        'arg_num': 2
    },
    'douyin': {
        'aliases': {'dylogo', '抖音logo', "douyin", "dy"},
        'func': create_douyin_logo,
        'arg_num': 1
    },
    'google': {
        'aliases': {'gglogo', '谷歌logo', "google"},
        'func': create_google_logo,
        'arg_num': 1
    }
}


async def create_logo(style: str, texts: List[str]) -> Union[str, bytes, BytesIO, Path]:
    try:
        func = commands[style]['func']
        return await func(*texts)
    except:
        logger.warning(traceback.format_exc(limit=1))
        return None
