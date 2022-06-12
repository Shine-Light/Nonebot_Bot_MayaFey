import os
import random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional
system_sep = os.sep
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import config, FORTUNE_PATH

'''
    抽签主题开关，当随机抽签时判断某主题是否开启
'''
MainThemeEnable = {
    "pcr":              config.pcr_flag,
    "genshin":          config.genshin_flag,
    "hololive":         config.hololive_flag,
    "touhou":           config.touhou_flag,
    "touhou_lostword":  config.touhou_lostword_flag,
    "touhou_old":       config.touhou_olg_flag,
    "onmyoji":          config.onmyoji_flag,
    "azure":            config.azure_flag,
    "asoul":            config.asoul_flag,
    "arknights":        config.arknights_flag,
    "granblue_fantasy": config.granblue_fantasy_flag,
    "punishing":        config.punishing_flag,
    "pretty_derby":     config.pretty_derby_flag,
    "dc4":              config.dc4_flag,
    "einstein":         config.einstein_flag,
    "sweet_illusion":   config.sweet_illusion_flag,
    "liqingge":         config.liqingge_flag,
    "hoshizora":        config.hoshizora_flag,
    "sakura":           config.sakura_flag
}
'''
    抽签主题对应表，第一键值为“抽签设置”或“主题列表”展示的主题名称
    Key-Value: 主题资源文件夹名-设置主题别名
'''
MainThemeList = {
    "random":   ["随机"],
    "pcr":      ["PCR", "公主链接", "公主连结", "Pcr", "pcr"],
    "genshin":  ["原神", "Genshin Impact", "genshin", "Genshin", "op", "原批"],
    "hololive": ["Hololive", "hololive", "Vtb", "vtb", "管人", "holo", "猴楼"],
    "touhou":   ["东方", "touhou", "Touhou", "车万"],
    "touhou_lostword":
                ["东方归言录", "东方lostword", "touhou lostword", "Touhou dlc"],
    "touhou_old": 
                ["旧东方", "旧版东方", "老东方", "老版东方", "经典东方"],
    "onmyoji":  ["阴阳师", "yys", "Yys", "痒痒鼠"],
    "azure":    ["碧蓝航线", "碧蓝", "azure", "Azure"],
    "asoul":    ["Asoul", "asoul", "a手", "A手", "as", "As"],
    "arknights":["明日方舟", "方舟", "arknights", "鹰角", "Arknights", "舟游"],
    "granblue_fantasy":
                ["碧蓝幻想", "Granblue Fantasy", "granblue fantasy", "幻想", "fantasy", "Fantasy"],
    "punishing":["战双", "战双帕弥什"],
    "pretty_derby":
                ["赛马娘", "马", "马娘", "赛马"],
    "dc4":      ["dc4", "DC4", "Dc4", "初音岛", "初音岛4"],
    "einstein": ["爱因斯坦携爱敬上", "爱因斯坦", "einstein", "Einstein"],
    "sweet_illusion":
                ["灵感满溢的甜蜜创想", "甜蜜一家人", "富婆妹"],
    "liqingge": ["李清歌", "清歌"],
    "hoshizora":["星空列车与白的旅行", "星空列车"],
    "sakura":   ["樱色之云绯色之恋", "樱云之恋", "樱云绯恋", "樱云"]
}

def copywriting() -> str:
    p = f"{FORTUNE_PATH}{system_sep}fortune{system_sep}copywriting.json"
    if not os.path.exists(p):
        return False

    with open(p, "r", encoding="utf-8") as f:
        content = json.load(f)

    return random.choice(content["copywriting"])

def getTitle(structure):
    p = f"{FORTUNE_PATH}{system_sep}fortune{system_sep}goodLuck.json"
    if not os.path.exists(p):
        return False

    with open(p, "r", encoding="utf-8") as f:
        content = json.load(f)

    for i in content["types_of"]:
        if i["good-luck"] == structure["good-luck"]:
            return i["name"]
    raise Exception("Configuration file error")

def randomBasemap(theme: str, spec_path: Optional[str]) -> str:
    try_time = 0
    if spec_path:
        _p = f"{FORTUNE_PATH}{system_sep}img"
        p = os.path.join(_p, spec_path)
        return p
    else:
        if theme == "random":
            __p = f"{FORTUNE_PATH}{system_sep}img"
            while True:
                picked_theme = random.choice(os.listdir(__p))
                if MainThemeEnable[picked_theme] == True:
                    break
                else:
                    try_time = try_time+1

                if try_time == len(MainThemeEnable):
                    break

            _p = os.path.join(__p, picked_theme)
            p = os.path.join(_p, random.choice(os.listdir(_p)))
        else:
            _p = os.path.join(f"{FORTUNE_PATH}{system_sep}img", theme)
            p = os.path.join(_p, random.choice(os.listdir(_p)))
        
        return p

def drawing(theme: str, spec_path: Optional[str], user_id: str, group_id: str) -> Path:
    fontPath = {
        "title": f"{FORTUNE_PATH}{system_sep}font{system_sep}Mamelon.otf",
        "text": f"{FORTUNE_PATH}{system_sep}font{system_sep}sakura.ttf",
    }
    imgPath = randomBasemap(theme, spec_path)
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = copywriting()
    title = getTitle(text)
    text = text["content"]
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath["title"], font_size)
    font_length = ttfront.getsize(title)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=ttfront,
    )
    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath["text"], font_size)
    result = decrement(text)
    if not result[0]:
        return
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(
            image_font_center[0]
            + (result[0] - 2) * font_size / 2
            + (result[0] - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)
    # Save
    outPath = exportFilePath(imgPath, user_id, group_id)
    img.save(outPath)
    return outPath

def exportFilePath(originalFilePath: str, user_id: str, group_id: str) -> Path:
    dirPath = f"{FORTUNE_PATH}{system_sep}out"
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    outPath = Path(originalFilePath).parent.parent.parent / "out" / f"{user_id}_{group_id}.png"
    return outPath

def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = " "
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [
                numberOfSlices,
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2) :],
            ]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [
                numberOfSlices,
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2) :],
            ]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality :])
        else:
            result.append(text[i * cardinality : (i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return "\n".join(list)