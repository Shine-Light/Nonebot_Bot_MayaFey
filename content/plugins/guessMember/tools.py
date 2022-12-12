"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/12/9 13:25
"""
import random

from io import BytesIO
from PIL import Image, ImageDraw
from utils.path import guessMember_cache_path


def S2B(text: str):
    if text in ["开", "是", "真", "true", "True"]:
        text = True
    elif text in ["关", "否", "假", "false", "False"]:
        text = False
    return text


def B2S(bool_: bool):
    if bool_:
        return "开"
    else:
        return "关"


def mosaic(img: bytes):
    width = 640
    height = 640
    granularity = 32

    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    img = Image.open(BytesIO(img))
    img = img.resize((width, height))

    for x in range(0, width, granularity):
        for y in range(0, height, granularity):
            r, g, b = img.getpixel((x, y))
            draw.rectangle([(x, y), (x + granularity, y + granularity)], fill=(r, g, b), outline=None)  # None即是不加网格

    image.save(guessMember_cache_path)


def cut(img: bytes, length: int):
    img = Image.open(BytesIO(img))
    x1 = y1 = random.randint(0, 640 - length)
    x2 = y2 = x1 + length
    img = img.crop((x1, y1, x2, y2))

    img.save(guessMember_cache_path)


def blur(img: bytes):
    img = Image.open(BytesIO(img))
    origin_size = img.size
    img = img.resize((8, 8))
    img = img.resize(origin_size)

    img.save(guessMember_cache_path)
