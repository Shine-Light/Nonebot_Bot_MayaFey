"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/7/22 11:28
"""
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from utils.other import add_target, translate
from utils.json_tools import json_write
from .tools import *


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "torment"),
    description="折磨群员,定时随机戳一戳",
    usage="/折磨群友 开启|关闭\n"
          "/折磨群友 定时|间隔 {小时}:{分钟}:{秒数}\n"
          "/折磨群友 配置|设置" + add_target(60)
)


torment_set = on_command("折磨群友", aliases={"折磨"}, priority=8)
@torment_set.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    gid = str(event.group_id)
    # 开关
    if len(args) == 1:
        if args[0] in ["开启", "开", "on"]:
            js = json_load(torment_config_path)
            try:
                state = js[gid]["state"]
            except KeyError:
                state = False
            if state:
                await torment_set.finish("已经开启过了哦")
            try:
                js.update({gid: {
                        "state": True,
                        "mode": js[gid]["mode"],
                        "time": js[gid]["time"]
                    }
                })
            # 群聊未设置过
            except KeyError:
                await torment_set.send("还没设置模式和时间哦,真宵先帮你设置吧,默认为 '间隔' 模式,时间为 '1' 小时")
                js.update({gid: {
                        "state": True,
                        "mode": "interval",
                        "time": "01:00:00"
                    }
                })
            json_write(torment_config_path, js)
            await add_job(gid)
            await torment_set.finish("设置成功")

        elif args[0] in ["关闭", "关", "off"]:
            js = json_load(torment_config_path)
            try:
                js.update({gid: {
                        "state": False,
                        "mode": js[gid]["mode"],
                        "time": js[gid]["time"]
                    }
                })
            # 未设置过
            except KeyError:
                await torment_set.finish("本群没有开启过此功能,所以不需要关闭哦")

            json_write(torment_config_path, js)
            await remove_job(gid)
            await torment_set.finish("设置成功")

        elif args[0] in ["设置", "配置", "setting", "config"]:
            await torment_set.send(get_config_text(gid))

        else:
            await torment_set.finish(f"没有 '{args[0]}' 选项,请检查命令")
    # 设置
    elif len(args) == 2:
        js = json_load(torment_config_path)
        mode = args[0]
        time = args[1]

        # 模式设置
        if mode == "间隔":
            mode = "interval"
        elif mode == "定时":
            mode = "cron"
        else:
            await torment_set.finish(f"没有 '{args[0]}' 选项,请检查命令")

        # 时间设置
        if "：" in time:
            await torment_set.finish("要用英文的 ':' 哦")
        if len(time.split(":")) == 3:
            # 异常处理
            try:
                hour = int(time.split(":")[0])
                minute = int(time.split(":")[1])
                second = int(time.split(":")[2])
            except:
                await torment_set.finish("真宵要的是整数哦")
            if hour < 0 or minute < 0 or second < 0:
                await torment_set.finish("真宵不会时光倒流,请用正数")
            if mode == "interval" and hour == 0 and minute == 0 and second == 0:
                await torment_set.finish("你想累死真宵吗?间隔最少1秒啦!")
            try:
                js.update({gid: {
                    "state": js[gid]["state"],
                    "mode": mode,
                    "time": time
                }})
            except KeyError:
                js.update({gid: {
                    "state": False,
                    "mode": mode,
                    "time": time
                }})

        else:
            await torment_set.finish("时间参数错误,格式也为 '{小时}:{分钟}:{秒数}'")

        json_write(torment_config_path, js)
        if js[gid]["state"]:
            await modify_job(gid)
            await torment_set.finish("修改成功")
        await torment_set.finish("设置成功")

    else:
        await torment_set.finish("参数长度有误,请检查命令")
