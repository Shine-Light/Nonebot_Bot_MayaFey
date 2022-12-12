"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/8/15 16:32
"""
import ujson as json
import pymysql
import datetime

from pathlib import Path
from nonebot import get_driver
from nonebot.log import logger
from utils.path import GenshinPray_path, GenshinPray_img_path
from utils.other import mk
from utils.htmlrender import template_to_pic, text_to_pic
from utils import json_tools
from content.plugins.credit.tools import minus
from .tools import Pray, Result, ResultCode, Assign, Query, Setting

fstr = "%Y-%m-%d %H:%M:%S"
try:
    config = get_driver().config
    host = config.mysql_host_genshin
    port = config.mysql_port_genshin
    user = str(config.mysql_user_genshin)
    password = str(config.mysql_password_genshin)
    database = str(config.mysql_db_genshin)
except:
    config = host = port = user = password = database = ""


class GenshinPray(object):
    connect = None
    cursor = None
    error = False

    def __init__(self):
        if not GenshinPray_path.exists():
            GenshinPray_path.mkdir(parents=True, exist_ok=True)
        if not GenshinPray_img_path.exists():
            GenshinPray_img_path.mkdir(parents=True, exist_ok=True)
        try:
            self.connect = pymysql.connect(host=host, port=port, user=user, password=password, autocommit=True)
            self.cursor = self.connect.cursor()
        except:
            logger.error("连接原神数据库失败,若无需该功能请忽略该提示")
            self.error = True

    async def init_with_gid(self, gid: str):
        """
        初始化,初始化错误时返回错误信息
        :param gid:群号
        """
        if not (GenshinPray_path / gid).exists():
            (GenshinPray_path / gid).mkdir(parents=True, exist_ok=True)
        if not (GenshinPray_path / gid / "config.json").exists():
            await mk("file", (GenshinPray_path / gid / "config.json"), "w", content=json.dumps({"cost": 1}))
        try:
            self.cursor.execute("USE genshinpray;")
            # 不存在授权码则创建新的授权码
            if not self.has_gid_token(gid):
                self.cursor.execute(f"INSERT INTO authorize values(null,'{gid}',99999,NOW(),'9999-12-31 23:59:59',0,0)")
        except Exception as e:
            return str(e)

    def has_gid_token(self, gid: str) -> bool:
        """
        群聊是否有授权码,被禁用或已过期的授权码视为不存在
        :param gid:群号
        """
        self.cursor.execute("SELECT Code, ExpireDate, IsDisable FROM authorize")
        result = self.cursor.fetchall()
        datetime_now = datetime.datetime.now()
        for re in result:
            datetime_expire = re[1]
            if re[0] == gid and datetime_expire > datetime_now and re[2] != 1:
                return True
        return False

    @staticmethod
    def set_one_cost(gid: str, cost: int) -> bool:
        """
        设置单抽所需积分数
        :param gid:群号
        :param cost:积分数
        """
        js = json_tools.json_load(GenshinPray_path / gid / "config.json")
        js.update({"cost": cost})
        json_tools.json_write(
            GenshinPray_path / gid / "config.json",
            js
        )
        return True

    @staticmethod
    def get_one_cost(gid: str) -> int:
        """
        获取单抽所需积分数
        :param gid:群号
        """
        return json_tools.json_load(GenshinPray_path / gid / "config.json")['cost']

    @staticmethod
    def get_ten_cost(gid: str):
        """
        获取十连所需积分数
        :param gid:群号
        """
        return GenshinPray.get_one_cost(gid)*10

    @staticmethod
    async def Pray(command: str, gid: str, uid: str, pondID: int, count: int, nickname: str = ""):
        """
        祈愿
        :param command:祈愿命令
        :param gid:群号
        :param uid:QQ号
        :param pondID:蛋池ID
        :param count:次数
        :param nickname:昵称
        """
        if count == 1:
            if not minus(gid, uid, GenshinPray.get_one_cost(gid)):
                return Result(ResultCode(-2), {})
        elif count == 10:
            if not minus(gid, uid, GenshinPray.get_ten_cost(gid)):
                return Result(ResultCode(-2), {})
        pray = Pray(
            command,
            gid,
            uid,
            nickname,
            pondID,
            1920,
            False
        )
        result = pray.get_result()
        result.imgUrl = GenshinPray_img_path / result.imgUrl
        return result

    @staticmethod
    def Assign(gid: str, uid: str, goodsName: str, nickname: str = ""):
        """
        武器定轨
        :param gid:群号
        :param uid:QQ号
        :param goodsName:武器名称
        :param nickname:昵称
        """
        assign = Assign(
            gid,
            uid,
            goodsName,
            nickname
        )
        return assign.Set_Assign()

    @staticmethod
    def get_Assign(gid: str, uid: str = ""):
        """
        查询定轨
        :param gid:群号
        :param uid:QQ号
        """
        query_Assign = Query(
            gid,
            uid
        )

        result = query_Assign.Get_Assign()
        if result.code.is_success():
            data = result.data
            message = f"当前定轨物品:{data['goodsName']}\n" \
                      f"类型:{data['goodsSubType']}\n" \
                      f"命定值:{data['assignValue']}"
            result.message = message

        return result

    @staticmethod
    def GetPondList(gid: str):
        """
        蛋池列表
        :param gid:群号
        """
        query_Assign = Query(
            gid,
        )

        result = query_Assign.GetPondInfo()
        if result.code.is_success():
            data = result.data
            roles = data['role']
            message = ""
            count = 0
            for role in roles:
                count += 1
                message += f"{role['pondIndex']}\n"
            message = "当前Up池列表:\n" + message
            message = f"总共有 {count} 个池子\n" + message
            result.message = message.strip("\n")

        return result

    @staticmethod
    async def GetRolePondInfo(gid: str, PondID: int):
        """
        获取指定蛋池UP信息
        :param gid:群号
        :param PondID:蛋池编号
        """
        query_Assign = Query(
            gid
        )

        result = query_Assign.GetPondInfo()
        if result.code.is_success():
            data = result.data
            roles = data['role']
            role = None
            for role_ in roles:
                if role_['pondIndex'] == PondID:
                    role = role_
                    break

            if not role:
                result.code.code = 606
            else:
                pondInfo = role['pondInfo']
                star5 = {
                    "name": pondInfo['star5UpList'][0]['goodsName'],
                    "ele": pondInfo['star5UpList'][0]['goodsSubType']
                }
                star41 = {
                    "name": pondInfo['star4UpList'][0]['goodsName'],
                    "ele": pondInfo['star4UpList'][0]['goodsSubType']
                }
                star42 = {
                    "name": pondInfo['star4UpList'][1]['goodsName'],
                    "ele": pondInfo['star4UpList'][1]['goodsSubType']
                }
                star43 = {
                    "name": pondInfo['star4UpList'][2]['goodsName'],
                    "ele": pondInfo['star4UpList'][2]['goodsSubType']
                }
                img = await template_to_pic(
                    str(Path(__file__).parent / "template" / "role_up"),
                    "index.html",
                    {
                        "star5": star5,
                        "star41": star41,
                        "star42": star42,
                        "star43": star43,
                    },
                    {
                        "viewport": {"width": 1920, "height": 900},
                        "base_url": f"file://{str(Path(__file__).parent / 'template' / 'arm_up')}"
                    }
                )
                result.imgUrl = img

        return result

    @staticmethod
    async def GetArmPondInfo(gid: str):
        """
        获取武器UP信息
        :param gid:群号
        """
        query_Assign = Query(
            gid,
        )

        result = query_Assign.GetPondInfo()
        if result.code.is_success():
            data = result.data
            pondInfo = data["arm"][0]["pondInfo"]

            star51 = {
                "name": pondInfo['star5UpList'][0]['goodsName'],
                "ele": pondInfo['star5UpList'][0]['goodsSubType']
            }
            star52 = {
                "name": pondInfo['star5UpList'][1]['goodsName'],
                "ele": pondInfo['star5UpList'][1]['goodsSubType']
            }
            star41 = {
                "name": pondInfo['star4UpList'][0]['goodsName'],
                "ele": pondInfo['star4UpList'][0]['goodsSubType']
            }
            star42 = {
                "name": pondInfo['star4UpList'][1]['goodsName'],
                "ele": pondInfo['star4UpList'][1]['goodsSubType']
            }
            star43 = {
                "name": pondInfo['star4UpList'][2]['goodsName'],
                "ele": pondInfo['star4UpList'][2]['goodsSubType']
            }
            star44 = {
                "name": pondInfo['star4UpList'][3]['goodsName'],
                "ele": pondInfo['star4UpList'][3]['goodsSubType']
            }
            star45 = {
                "name": pondInfo['star4UpList'][4]['goodsName'],
                "ele": pondInfo['star4UpList'][4]['goodsSubType']
            }
            img = await template_to_pic(
                str(Path(__file__).parent / "template" / "arm_up"),
                "index.html",
                {
                    "star51": star51,
                    "star52": star52,
                    "star41": star41,
                    "star42": star42,
                    "star43": star43,
                    "star44": star44,
                    "star45": star45
                },
                {
                    "viewport": {"width": 1920, "height": 900},
                    "base_url": f"file://{str(Path(__file__).parent / 'template' / 'arm_up')}"
                }
            )
            result.imgUrl = img

        return result

    @staticmethod
    async def GetMemberPrayDetail(gid: str, uid: str):
        """
        获取成员祈愿信息
        :param gid:群号
        :param uid:QQ号
        """
        query = Query(
            gid,
            uid
        )

        result = query.GetPrayDetail()

        if result.code.is_success() and result.data:
            data = result.data
            message = f"你的祈愿信息:\n" \
                      f"总祈愿次数: {data['totalPrayTimes']}\n" \
                      f"角色池距离小保底还有 {data['role90Surplus']} 发\n" \
                      f"角色池距离大保底还有 {data['role180Surplus']} 发\n" \
                      f"武器池距离保底还有 {data['arm80Surplus']} 发\n" \
                      f"常驻池距离保底还有 {data['perm90Surplus']} 发\n" \
                      f"武器池命定值: {data['armAssignValue']}\n" \
                      f"角色池祈愿次数: {data['rolePrayTimes']}\n" \
                      f"武器池祈愿次数: {data['armPrayTimes']}\n" \
                      f"常驻池祈愿次数: {data['permPrayTimes']}\n" \
                      f"累计获得4星物品次数: {data['star4Count']}\n" \
                      f"累计获得5星物品次数: {data['star5Count']}\n" \
                      f"角色池累计获得4星物品数量: {data['roleStar4Count']}\n" \
                      f"武器池累计获得4星物品数量: {data['armStar4Count']}\n" \
                      f"常驻池累计获得4星物品数量: {data['permStar4Count']}\n" \
                      f"角色池累计获得5星物品数量: {data['roleStar5Count']}\n" \
                      f"武器池累计获得5星物品数量: {data['armStar5Count']}\n" \
                      f"常驻池累计获得5星物品数量: {data['permStar5Count']}\n" \
                      f"4星出货率: {data['star4Rate']}\n" \
                      f"5星出货率: {data['star5Rate']}\n" \
                      f"角色池4星出货率(%): {data['roleStar4Rate']}\n" \
                      f"武器池4星出货率(%): {data['armStar4Rate']}\n" \
                      f"常驻池4星出货率(%): {data['permStar4Rate']}\n" \
                      f"角色池5星出货率(%): {data['roleStar5Rate']}\n" \
                      f"武器池5星出货率(%): {data['armStar5Rate']}\n" \
                      f"常驻池5星出货率(%): {data['permStar5Rate']}"

            img = await text_to_pic(message)
            result.imgUrl = img
            return result

    @staticmethod
    def GetMemberPrayRecord(gid: str, uid: str):
        """
        获取成员祈愿记录
        :param gid:群号
        :param uid:QQ号
        """
        query = Query(
            gid,
            uid
        )

        result = query.GetPrayRecord()
        message = []
        if result.code.is_success() and result.data:
            data = result.data
            star5 = data['star5']['all']
            star4 = data['star4']['all']
            for s in star5:
                temp = f"出货时间:{s['createDate']}\n" \
                       f"星级:{s['rareType']}\n" \
                       f"类型:{s['goodsType']}\n" \
                       f"名称:{s['goodsName']}\n" \
                       f"消耗抽数:{s['cost']}\n"
                message.append(temp)
            for s in star4:
                temp = f"出货时间:{s['createDate']}\n" \
                       f"星级:{s['rareType']}\n" \
                       f"类型:{s['goodsType']}\n" \
                       f"名称:{s['goodsName']}\n" \
                       f"消耗抽数:{s['cost']}\n"
                message.append(temp)
            result.message = message

        return result

    @staticmethod
    def GetLuckRanking(gid: str):
        """
        获取成员祈愿记录
        :param gid:群号
        """
        query = Query(
            gid,
        )

        result = query.GetLuckRanking()
        if result.code.is_success() and result.data:
            data = result.data
            star5 = data['star5Ranking'][:3]
            star4 = data['star4Ranking'][:3]
            message = "五星排行榜:\n"
            for s in star5:
                message += f"  成员ID:{s['memberCode']}\n" \
                           f"\t成员昵称:{s['memberName']}\n" \
                           f"\t累计获取5星数量:{s['count']}\n" \
                           f"\t总祈愿次数:{s['totalPrayTimes']}\n" \
                           f"\t5星出货率:{s['rate']}\n"
            message += "四星排行榜:\n"
            for s in star4:
                message += f"  成员ID:{s['memberCode']}\n" \
                           f"\t成员昵称:{s['memberName']}\n" \
                           f"\t累计获取4星数量:{s['count']}\n" \
                           f"\t总祈愿次数:{s['totalPrayTimes']}\n" \
                           f"\t4星出货率:{s['rate']}\n"

            result.message = message.strip("\n")

        return result

    @staticmethod
    def SetRolePond(gid: str, pondId: str, roles: list):
        """
        自定义角色池,蛋池不存在时自动创建
        :param gid:群号
        :param pondId:蛋池编号
        :param roles:角色列表
        """
        setting = Setting(
            gid,
            {
                "pondIndex": pondId,
                "upItems": roles
            }
        )

        result = setting.SetRolePond()
        return result

    @staticmethod
    def SetArmPond(gid: str, arms: list):
        """
        自定义角色池,蛋池不存在时自动创建
        :param gid:群号
        :param arms:武器列表
        """
        setting = Setting(
            gid,
            {
                "upItems": arms
            }
        )
        result = setting.SetArmPond()

        if not result.code.is_success():
            result.code.msg = result.source['message']

        return result

    @staticmethod
    def ResetRolePond(gid: str):
        """
        清空角色池
        :param gid:群号
        """
        setting = Setting(
            gid
        )

        result = setting.ResetRolePond()

        return result

    @staticmethod
    def ResetArmPond(gid: str):
        """
        清空武器池
        :param gid:群号
        """
        setting = Setting(
            gid
        )

        result = setting.ResetArmPond()

        return result

    @staticmethod
    def SetSkinRate(gid: str, rare: int):
        """
        清空武器池
        :param gid:群号
        :param rare:概率
        """
        setting = Setting(
            gid,
            {"rare": rare}
        )

        result = setting.SetSkinRate()

        return result
