"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/6/3 16:46
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.exception import FinishedException, ActionFailed
from nonebot.log import logger

from utils.other import add_target
from nonebot.plugin import PluginMetadata


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="saymoney",
    description="支付宝到账XX元",
    usage="/到账 {金额}" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "到账语音生成",
    }
)


api_alipay_url = "https://mm.cqu.cc/share/zhifubaodaozhang/?money="
api_wx_url = "W.I.P"

saymoney = on_command(cmd="到账", priority=8)
@saymoney.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        args = args.extract_plain_text()
        try:
            args = int(args)
        except (ValueError, TypeError):
            try:
                args = float(args)
            except (ValueError, KeyError):
                await saymoney.finish("参数错误,参数可能不是数字")

        if 0.01 > float(args) or float(args) > 999999999999.99:
            print(args)
            await saymoney.finish("金额超出范围")

        url = api_alipay_url + f"{args}.mp3"
        await saymoney.send(MessageSegment.record(url))

    except FinishedException:
        pass
    except ActionFailed:
        await saymoney.send("发送失败,环境错误或账号风控")
        logger.warning("账号风控")
    except Exception as e:
        await saymoney.send(f"出现未知错误:{str(e)}")
