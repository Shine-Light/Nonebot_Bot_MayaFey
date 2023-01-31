"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/29 12:53
"""
import re
import ujson as json

from nonebot import on_regex, on_message, on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg, RegexGroup
from nonebot.plugin import PluginMetadata
from utils.path import *
from utils import json_tools, users, database_mysql
from utils.permission import special_per, permission_
from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "question"),
    description="问答",
    usage="精准问{问题}答{回答} (超级用户)\n"
          "模糊问{问题}答{回答} (超级用户)\n"
          "正则问{问题}答{回答} (超级用户)\n"
          "/问答列表\n"
          "/问答删除 {问题} (超级用户)" + add_target(60),
    extra={
        "permission_special": {
            "question_vague": "superuser",
            "question_absolute": "superuser",
            "question_regular": "superuser"
        }
    }
)


cursor = database_mysql.cursor
command_start = "".join(get_driver().config.command_start)


# 添加问答(模糊)
question_vague = on_regex(rf"^([{command_start}]?模糊问)(.*)答([\s\S])*", priority=13, block=False)
@question_vague.handle()
async def _(bot: Bot, event: GroupMessageEvent, group: tuple = RegexGroup()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "question_vague", gid):
        Question = group[1]
        Answer = group[2]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json_tools.json_load(question_path)
        if not Question:
            await question_vague.finish("添加失败,无问题")
        if not Answer:
            await question_vague.finish("添加失败,无回答")
        try:
            vague = QAs.get("vague")
            if vague is None:
                vague = {}
            vague.update({Question: Answer})
            json_tools.json_update(question_path, "vague", json.dumps(vague))
            await question_vague.send('添加成功')

        except Exception as e:
            await question_vague.send('添加失败:' + str(e))

    else:
        await question_vague.send("无权限")


# 添加问答(精准)
question_absolute = on_regex(rf"^([{command_start}]?精准问)(.*)答([\s\S])*", priority=13, block=False)
@question_absolute.handle()
async def _(bot: Bot, event: GroupMessageEvent, group: tuple = RegexGroup()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "question_absolute", gid):
        Question = group[1]
        Answer = group[2]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json_tools.json_load(question_path)
        if not Question:
            await question_absolute.finish("添加失败,无问题")
        if not Answer:
            await question_absolute.finish("添加失败,无回答内容")
        try:
            absolute = QAs.get("absolute")
            if absolute is None:
                absolute = {}
            absolute.update({Question: Answer})
            json_tools.json_update(question_path, "absolute", json.dumps(absolute))
            await question_absolute.send('添加成功')

        except Exception as e:
            await question_absolute.send('添加失败:' + str(e))

    else:
        await question_absolute.send("无权限")


# 添加问答(正则)
question_regular = on_regex(rf"^([{command_start}]?正则问)(.*)答([\s\S])*", priority=13, block=False)
@question_regular.handle()
async def _(bot: Bot, event: GroupMessageEvent, group: tuple = RegexGroup()):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "question_regular", gid):
        Question = group[1]
        Answer = group[2]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json_tools.json_load(question_path)
        if not Question:
            await question_regular.finish("添加失败,无问题")
        if not Answer:
            await question_regular.finish("添加失败,无回答内容")
        try:
            regular = QAs.get("regular")
            if regular is None:
                regular = {}
            regular.update({Question: Answer})
            json_tools.json_update(question_path, "regular", json.dumps(regular))
            await question_regular.send('添加成功')
        except Exception as e:
            await question_regular.send('添加失败:' + str(e))

    else:
        await question_regular.send("无权限")


# 问答检测
ques_in = on_message(priority=12, block=False)
@ques_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    question_path = question_base / f"{gid}.json"
    qas: dict = json_tools.json_load(question_path)
    if not qas:
        return
    A = ""
    meta_msg = str(event.get_message())

    # 优先匹配精准,再匹配正则,最后再匹配模糊
    absolute: dict = qas.get("absolute")
    if absolute:
        for question in absolute:
            if str(question) == meta_msg:
                A = absolute[question]
                break

    regular: dict = qas.get("regular")
    if regular and not A:
        for question in regular:
            if re.findall(question, meta_msg):
                A = regular[question]
                break

    vague: dict = qas.get("vague")
    if vague and not A:
        for question in vague:
            if str(question) in meta_msg:
                A = vague[question]
                break

    if A:
        messages = A
        await ques_in.send(Message(messages))


# 其他功能(删除,查看)
ques_more = on_command(cmd="问答", aliases={"自定义问答"}, priority=5, block=False)
@ques_more.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    uid = str(event.user_id)
    gid = str(event.group_id)
    question_path = question_base / f"{gid}.json"
    qas = json_tools.json_load(question_path)
    msg = ""
    args = args.extract_plain_text()
    mode = args.split(" ", 1)[0]
    if mode == "列表":
        vague: dict = qas.get("vague")
        if vague:
            msg += "模糊问答:\n"
            for qa in vague:
                msg += "\t" + qa + "\n"

        absolute: dict = qas.get("absolute")
        if absolute:
            msg += "精准问答:\n"
            for qa in absolute:
                msg += "\t" + qa + "\n"

        regular: dict = qas.get("regular")
        if regular:
            msg += "正则问答:\n"
            for qa in regular:
                msg += "\t" + qa + "\n"

        if not msg:
            msg = "无问答内容"
        else:
            msg = msg[:-1]

    elif mode == "删除" or mode == "-":
        find = False
        gid = str(event.group_id)
        role = users.get_role(gid, uid)
        # 成员无权限添加/删除
        if permission_(role, "superuser"):
            content = args.split(" ", 1)[1]

            for qaS in qas:
                if find:
                    break
                for qa in list(qas[qaS]):
                    if content == qa:
                        qas[qaS].pop(content)
                        msg = "删除成功"
                        find = True
                        break

                    else:
                        msg = "删除失败,没有该问题"

                qas.update({qaS: qas[qaS]})
                json_tools.json_write(question_path, qas)

        else:
            await ques_more.send("无权限")

    else:
        msg = "没有该模式"

    await ques_more.send(msg)
