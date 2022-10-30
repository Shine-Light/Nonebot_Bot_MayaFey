"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/29 12:53
"""
import json

from nonebot.params import CommandArg
from nonebot import on_regex, on_message, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
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
          "/问答列表"
          "/问答删除 {问题} (超级用户)" + add_target(60)
)


cursor = database_mysql.cursor


# 添加问答(模糊)
question_vague = on_regex("^模糊问.*?(答)", priority=5)
@question_vague.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "question", gid):
        msg_meta = str(event.get_message())
        Question = msg_meta.split("问", 1)[1].split("答", 1)[0]
        Answer = msg_meta.split("答", 1)[1]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json_tools.json_load(question_path)
        if not Question:
            await question_vague.finish("添加失败,无问题")
        if not Answer:
            await question_vague.finish("添加失败,无回答")
        try:
            vague = QAs["vague"]
            vague.update({Question: Answer})
            QAs.update({"vague": vague})
            with open(question_path, 'w', encoding="utf-8") as file:
                file.write(json.dumps(QAs, ensure_ascii=False))
            await question_vague.send('添加成功')

        except Exception as e:
            await question_vague.send('添加失败:' + str(e))

    else:
        await question_vague.send("无权限")


# 添加问答(精准)
question_absolute = on_regex("^精准问.*?(答)", priority=5)
@question_absolute.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if special_per(role, "question_absolute", gid):
        msg_meta = str(event.get_message())
        Question = msg_meta.split("问", 1)[1].split("答", 1)[0]
        Answer = msg_meta.split("答", 1)[1]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json_tools.json_load(question_path)
        if not Question:
            await question_vague.finish("添加失败,无问题")
        if not Answer:
            await question_absolute.finish("添加失败,无回答内容")
        try:
            absolute = QAs["absolute"]
            absolute.update({Question: Answer})
            QAs.update({"absolute": absolute})
            with open(question_path, 'w', encoding="utf-8") as file:
                file.write(json.dumps(QAs, ensure_ascii=False))
            await question_absolute.send('添加成功')

        except Exception as e:
            await question_absolute.send('添加失败:' + str(e))

    else:
        await question_absolute.send("无权限")


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

    try:
        absolute: dict = qas["absolute"]
    except KeyError:
        absolute = None
    if absolute:
        for qa in absolute:
            if str(qa) == meta_msg:
                A = absolute[qa]
                break

    try:
        vague: dict = qas["vague"]
    except KeyError:
        vague = None
    if vague:
        for qa in vague:
            if str(qa) in meta_msg:
                A = vague[qa]
    if A:
        messages = A
        await ques_in.send(Message(messages))


# 其他功能(删除,查看)
ques_more = on_command(cmd="问答", aliases={"自定义问答"}, priority=5)
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
        try:
            vague: dict = qas["vague"]
        except KeyError:
            vague = None
        if vague:
            msg += "模糊问答:\n"
            for qa in vague:
                msg += "\t" + qa + "\n"

        try:
            absolute: dict = qas["absolute"]
        except KeyError:
            absolute = None
        if absolute:
            msg += "精准问答:\n"
            for qa in absolute:
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
