import random
from pathlib import Path

from nonebot import on_endswith, on_startswith
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from utils.other import add_target, translate

import ujson as json


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "answersbook"),
    description="愿一切无解都有解！解除你的迷惑，终结你的纠结！",
    usage="翻看答案{问题}\n"
          "{问题}翻看答案"  + add_target(60)
)


answers_path = Path(__file__).parent / "answersbook.json"
answers = json.loads(answers_path.read_text("utf-8"))


def get_answers():
    key = random.choice(list(answers))
    return answers[key]["answer"]


answers_starts = on_startswith("翻看答案")
answers_ends = on_endswith("翻看答案")


@answers_starts.handle()
@answers_ends.handle()
async def answersbook(event: GroupMessageEvent, matcher: Matcher):
    msg = event.message.extract_plain_text().replace("翻看答案", "")
    if not msg:
        await matcher.finish("你想问什么问题呢？")
    answer = get_answers()
    await matcher.send(answer, at_sender=True)
