import shlex
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from .data_source import create_logo, commands

__help__plugin_name__ = 'logo'
__des__ = 'logo生成'
__cmd__ = '''
P站：/ph {文本1} {文本2}
youtube：/yt {文本1} {文本2}
5000兆円欲しい!：/5000兆 {文本1} {文本2}
抖音：/douyin {文本}
谷歌：/google {文本}
'''.strip()
__short_cmd__ = 'ph、yt、5000兆、douyin'
__example__ = '''
/ph Porn Hub
/yt You Tube
/5000兆 我去 初音未来
/douyin douyin
'''.strip()
__usage__ = f'{__des__}\n使用:\n{__cmd__}\n示例:\n{__example__}'


async def handle(matcher: Matcher, style: str, text: str):
    arg_num = commands[style]['arg_num']
    texts = [text] if arg_num == 1 else shlex.split(text)
    if len(texts) != arg_num:
        await matcher.finish('参数数量不符')

    image = await create_logo(style, texts)
    if image:
        await matcher.finish(MessageSegment.image(image))
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():
    def create_handler(style: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            text = msg.extract_plain_text().strip()
            if not text:
                await matcher.finish()
            await handle(matcher, style, text)

        return handler

    for style, params in commands.items():
        matcher = on_command(style, aliases=params['aliases'],
                             priority=9, block=True)
        matcher.append_handler(create_handler(style))


create_matchers()


helps = on_command(cmd="logo", aliases={"Logo"}, priority=9, block=True)
@helps.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    cmd = str(event.get_message()).split(" ", 1)
    if len(cmd) < 2:
        await helps.finish(__usage__)
    cmd = cmd[1]
    if cmd == "帮助" or cmd == "help":
        await helps.finish(__usage__)
