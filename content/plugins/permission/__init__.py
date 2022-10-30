"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/30 20:36
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from utils import database_mysql
from utils import users, admin_tools
from utils.other import add_target, translate
from utils.permission import special_per, role_en, role_cn, get_special_per


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "permission"),
    description="设置和查看权限",
    usage="/我的权限\n"
          "/权限设置 @xx {权限等级} (超级用户)" + add_target(60)
)

cursor = database_mysql.cursor
db = database_mysql.connect


per = on_command(cmd="权限设置", aliases={"perset", "设置权限"}, priority=2)
@per.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role_sender = users.get_role(gid, str(event.user_id))
    sb = admin_tools.At(event.json())
    if not sb:
        msg = str(event.get_message()).split(" ")
        if len(msg) != 3:
            await per.finish("指令错误")
        sb.append(msg[1])
    if special_per(role_sender, "per", gid):
        msg_split = str(event.get_message()).split(" ", 2)
        if len(msg_split) != 3:
            await per.finish("指令错误")
        uid_sender = str(event.user_id)
        sender_role = users.get_role(gid, uid_sender)
        role = str(event.get_message()).split(" ")[-1].strip()
        roles_cn = ["根用户", "群主", "管理员", "超级用户", "成员", "黑名单"]
        roles_en = ["Van", "owner", "admin", "superuser", "member", "baned"]
        for uid in sb:
            uid = str(uid)
            cursor.execute(f"SELECT uid,role FROM users WHERE uid='{uid}' AND gid='{gid}';")
            re = cursor.fetchone()
            user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
            nickname = user['nickname']
            if re:
                if uid_sender == uid:
                    await per.finish("不可设置自己的权限")

                if role_en(role) == "superuser" and sender_role == role_en(role):
                    await per.finish("超级用户无法设置超级用户")

                if role_en(role) == "owner" or role_en(role) == "Van" or role_en(role) == "admin":
                    await per.finish(f"{role} 不可设置")

                if role_cn(role) == re[1] or role_en(role) == re[1]:
                    await per.finish(f"用户 {nickname} 已经是 {role} 了")

                if (role in roles_cn) or (role in roles_en):
                    if users.update_role(gid, uid, role_en(role)):
                        await per.finish(f"修改 {nickname} 权限成功")
                    else:
                        await per.finish("修改出错")
                else:
                    await per.finish("没有该等级")

            else:
                await per.finish(f"用户 {uid} 不存在")
    else:
        await per.send(f"权限不足,权限需在 {get_special_per(gid, 'per')} 及以上")


my_per = on_command(cmd="我的权限", priority=8)
@my_per.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role_sender = users.get_role(gid, str(event.user_id))
    if special_per(role_sender, "my_per", gid):
        uid = str(event.user_id)
        role = users.get_role(gid, uid)
        role = role_cn(role)
        await my_per.send(f"你的等级为:{role}", at_sender=True)

    else:
        await per.send(f"权限不足,权限需在 {get_special_per(gid, 'my_per')} 及以上")
