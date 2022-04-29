"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/30 20:36
"""
from . import tools
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from ..utils import database_mysql
from ..utils import users, admin_tools


cursor = database_mysql.cursor
db = database_mysql.connect


per = on_command(cmd="权限设置", aliases={"perset"}, priority=2)
@per.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role_sender = users.get_role(gid, str(event.user_id))
    sb = admin_tools.At(event.json())
    t = True
    if not sb:
        msg = str(event.get_message()).split(" ")
        if len(msg) != 3:
            await per.finish("指令错误")
        sb.append(msg[1])
    if tools.special_per(role_sender, "per", gid):
        msg_split = str(event.get_message()).split(" ", 2)
        if len(msg_split) != 3:
            await per.finish("指令错误")
        uid_sender = str(event.user_id)
        role = str(event.get_message()).split(" ")[-1].strip()
        role_cn = ["群主", "管理员", "超级用户", "成员", "黑名单"]
        role_en = ["Van", "owner", "admin", "superuser", "member", "baned"]
        for uid in sb:
            uid = str(uid)
            cursor.execute(f"SELECT uid,role FROM users WHERE uid='{uid}' AND gid='{gid}';")
            re = cursor.fetchone()
            user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
            nickname = user['nickname']
            if re:
                if uid_sender == uid:
                    await per.send("不可设置自己的权限")
                    t = False

                if (tools.role_en(role) == "owner" or tools.role_en(role) == "Van" or tools.role_en(role) == "admin") and t:
                    await per.finish(f"{role} 不可设置")

                if tools.role_cn(role) == re[1] or tools.role_en(role) == re[1]:
                    await per.send(f"用户 {nickname} 已经是 {role} 了")
                    t = False

                if (role in role_cn) or (role in role_en):
                    if not t:
                        pass
                    elif users.update_role(gid, uid, tools.role_en(role)):
                        await per.send(f"修改 {nickname} 权限成功")
                    else:
                        await per.send("修改出错")
                else:
                    await per.send("没有该等级")

            else:
                await per.send(f"用户 {uid} 不存在")
    else:
        await per.send("权限不足,权限需在 管理员 及以上")

my_per = on_command(cmd="我的权限", priority=8)
@my_per.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role_sender = users.get_role(gid, str(event.user_id))
    if tools.special_per(role_sender, "my_per", gid):
        uid = str(event.user_id)
        role = users.get_role(gid, uid)
        role_cn = tools.role_cn(role)
        await my_per.send(f"你的等级为:{role_cn}", at_sender=True)

    else:
        await my_per.send("无权限")
