"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 21:10
"""


from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from .functions import *
from ..withdraw import add_target
from ..utils.path import *
from ..utils import htmlrender


control = on_command(cmd="插件控制", priority=4)
@control.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 不可关闭插件
    not_set: list = open(unset_path, 'r', encoding="utf-8").read().split(",")
    url = control_path / str(event.group_id) / "control.json"
    plugin_config = json_tools.json_load(url)
    args = args.extract_plain_text()
    cmd: str = args.split(' ', 1)[0]
    message = ''
    cmd_cn = translate('e2c', cmd)
    cmd_en = translate('c2e', cmd)
    line = 1
    # 查看插件状态
    if cmd == '状态':
        plugin_list: str = '插件默认全开,插件开关状态:\n'
        for plugin in plugin_config:
            plugin_cn = translate('e2c', plugin)
            # 开状态
            if plugin_config[plugin]:
                # 占位符不显示
                if plugin == "test":
                    pass
                # 不可关闭插件
                elif plugin in not_set:
                    pass
                else:
                    if line % 3 == 0:
                        plugin_list += f'{plugin_cn}: 开\n'
                    else:
                        plugin_list += f'{plugin_cn}: 开    '
                    line += 1
            # 关状态
            else:
                if line % 3 == 0:
                    plugin_list += f'{plugin_cn}: 关\n'
                else:
                    plugin_list += f'{plugin_cn}: 关    '
                line += 1
        message += plugin_list
        message = message
        await control.send(message=Message([MessageSegment.image(await htmlrender.text_to_pic(message)),
                                            MessageSegment.text("已隐藏不可设置插件")]))

    # 控制插件开关
    else:
        if cmd_en in plugin_config:
            if cmd_en in not_set:
                message = f'插件 {cmd_cn} 不可关闭'
            elif plugin_config[cmd_en]:
                plugin_config.update({cmd_en: False})
                message = f'插件 {cmd_cn} 已关闭'
            else:
                plugin_config.update({cmd_en: True})
                message = f'插件 {cmd_cn} 已开启'
            json_tools.json_write(url, plugin_config)
        else:
            message = '找不到该插件'

        await control.send(message=Message([MessageSegment.text(message)]))

