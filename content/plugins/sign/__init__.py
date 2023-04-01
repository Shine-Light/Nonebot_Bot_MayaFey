"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/22 22:27
"""
import time
import datetime


from httpx import HTTPError
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from utils import database_mysql, time_tools, requests_tools, users
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from . import tools
from content.plugins import credit

from utils.other import add_target, translate


# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="sign",
    description="签到",
    usage="/签到" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "签到",
    }
)

ftr: str = "%Y-%m-%d"
# 数据库游标
db = database_mysql.connect
cursor = database_mysql.cursor


# 签到主函数
def daySign(gid: str, uid: str) -> dict:
    try:
        date_now = datetime.datetime.strftime(datetime.datetime.now(), ftr)
        date_last = users.get_dateLast(gid, uid)
        if date_last == date_now:
            return {"result": "signed"}
        count_all = users.get_countAll(gid, uid) + 1
        count_continue = users.get_countContinue(gid, uid) + 1
        if time_tools.date_calc(date_last, date_now) != 1:
            count_continue = 1
        sql_update = f"UPDATE sign SET date_last='{date_now}',count_all={count_all},count_continue={count_continue} WHERE uid='{uid}' AND gid='{gid}';"
        cursor.execute(sql_update)
        db.commit()
        credits = credit.tools.added(10, count_continue)
        credit.tools.add(gid, uid, credits)
        return {"result": "success", "credit": credits}
    except Exception as e:
        return {"result": "error", "message": str(e)}


sign = on_command(cmd='签到', aliases={'打卡', 'sign'}, priority=7)
@sign.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    re = daySign(gid, uid)
    try:
        if re['result'] == "success":
            credit = re['credit']
            time_now = time.strftime("%H:%M:%S", time.localtime())
            img = await requests_tools.get_img_bytes(await requests_tools.match_30X('https://www.dmoe.cc/random.php'))
            await sign.send(message=Message([
                MessageSegment.text(f'签到成功, 当前时间: {time_now}, 你已连续签到{users.get_countContinue(gid, uid)}天, 获得积分{credit}'),
                MessageSegment.image(file=img)
            ]), at_sender=True)
        elif re['result'] == 'signed':
            await sign.send('你今天已经签到过了哦', at_sender=True)
        else:
            await sign.send("未知异常:" + re.get('message'))
    except (ConnectionError, HTTPError):
        await sign.send("网络出现异常,无法获取图片,但不影响签到")
    except Exception as e:
        await sign.send("未知异常:" + str(e))
