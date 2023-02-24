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
from utils.permission import special_per, role_en, role_cn, get_special_per, permissions, permission_, get_lev, matcherPers


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "permission"),
    description="设置和查看权限",
    usage="/我的权限\n"
          "/权限设置 @xx {权限等级} (超级用户)" + add_target(60),
    extra={
        "permission_common": "baned",
        "permission_special": {
            "permission:per": "superuser"
        }
    }
)

cursor = database_mysql.cursor
db = database_mysql.connect
special_permissions = ["Van", "owner", "admin"]


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

    msg_split = str(event.get_message()).split(" ", 2)
    if len(msg_split) != 3:
        await per.finish("指令错误")
    uid_sender = str(event.user_id)
    sender_role = users.get_role(gid, uid_sender)
    role = str(event.get_message()).split(" ")[-1].strip()
    for uid in sb:
        uid = str(uid)
        cursor.execute(f"SELECT uid,role FROM users WHERE uid='{uid}' AND gid='{gid}';")
        re = cursor.fetchone()
        target_role = re[1]
        user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
        nickname = user['nickname']
        if re:
            if uid_sender == uid:
                await per.finish("不可设置自己的权限")

            if permission_(role, sender_role):
                await per.finish("只能设置级别小于自己的权限")

            if role_en(role) in special_permissions:
                await per.finish(f"{role} 为特殊权限,不可设置")

            if target_role in special_permissions:
                await per.finish(f"{nickname} 的权限为特殊权限,不可设置")

            if role_cn(role) == target_role or role_en(role) == target_role:
                await per.finish(f"用户 {nickname} 已经是 {role} 了")

            if role_en(role) in permissions:
                if users.update_role(gid, uid, role_en(role)):
                    await per.finish(f"成功修改 {nickname} 权限为 {role_cn(role)}")
                else:
                    await per.finish("修改出错")
            else:
                await per.finish("没有该权限")

        else:
            await per.finish(f"用户 {uid} 不存在")
matcherPers.addMatcher("permission:per", per)

my_per = on_command(cmd="我的权限", priority=8)
@my_per.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    role_sender = users.get_role(gid, str(event.user_id))
    if special_per(role_sender, "my_per", gid):
        uid = str(event.user_id)
        role = users.get_role(gid, uid)
        role = role_cn(role)
        level = get_lev(role)
        await my_per.send(f"你的权限为:{role}\n"
                          f"你的级别为:{level}", at_sender=True)
