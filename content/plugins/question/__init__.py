"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/29 12:53
"""
import json

from nonebot import on_regex, on_message, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from ..utils.path import *
from ..utils import json_tools, users, database_mysql
from .. import permission


cursor = database_mysql.cursor


# 添加问答
question = on_regex("^[(?<=问).{1,}(?=答)]", priority=5)


@question.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role = users.get_role(gid, str(event.user_id))
    if permission.tools.special_per(role, "question", gid):
        msg_meta = str(event.get_message())
        Question = msg_meta.split("问", 1)[1].split("答", 1)[0]
        Answer = msg_meta.split("答", 1)[1]
        question_path = question_base / f"{gid}.json"
        QAs: dict = json.loads(open(question_path, 'r', encoding='utf-8').read())
        if not Answer:
            await question.finish("添加失败,无回答内容")
        try:
            QAs.update({Question: Answer})
            with open(question_path, 'w', encoding="utf-8") as file:
                file.write(json.dumps(QAs, ensure_ascii=False))
            #
            await question.send('添加成功')

        except Exception as e:
            await question.send('添加失败:' + str(e))

    else:
        await question.send("无权限")


# 问答检测
ques_in = on_message(priority=12)
@ques_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    question_path = question_base / f"{gid}.json"
    qa: dict = json_tools.json_load(question_path)
    # A: list = []
    A = ""
    meta_msg = str(event.get_message())
    for Q in qa:
        if Q in meta_msg:
            A = qa[Q]
            break
    if A:
        messages = A
        await ques_in.send(Message(messages))


# 其他功能(删除,查看)
ques_more = on_command(cmd="问答", aliases={"自定义问答"}, priority=5)
@ques_more.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    question_path = question_base / f"{gid}.json"
    meta_msg = str(event.get_message())
    mode = meta_msg.split("答", 1)[1].split(" ", 1)[0]
    qas = json_tools.json_load(question_path)
    msg = ""
    if mode == "列表":
        for qa in qas:
            if qa != "test":
                msg += qa + "\n"

        if not msg:
            msg = "无问答内容"
        else:
            msg = "问题列表:\n" + msg
            msg = msg[:-1]

    elif mode == "删除" or mode == "-":
        # 成员无权限添加/删除
        gid = str(event.group_id)
        role = users.get_role(gid, uid)
        if permission.tools.permission_(role, "superuser"):
            content = meta_msg.split(" ", 1)[1]

            if content in qas:
                qas.pop(content)
                json_tools.json_write(question_path, qas)
                msg = "删除成功"

            else:
                msg = "删除失败,没有该插件"

        else:
            await ques_more.send("无权限")

    else:
        msg = "没有该模式"

    await ques_more.send(msg)
