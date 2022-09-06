"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/8/15 17:01
"""
import json
import requests

from nonebot import get_driver

config = get_driver().config
try:
    api_host = config.genshin_host
    api_port = config.genshin_port
    api_ssl = config.genshin_ssl
    if api_ssl:
        api_ssl = "https"
    else:
        api_ssl = "http"
    api_url = f"{api_ssl}://{api_host}:{api_port}"
except:
    api_url = ""


class CommandUrl(object):
    # 祈愿
    RolePray_One = "/api/RolePray/PrayOne"  # 角色池单抽
    RolePray_Ten = "/api/RolePray/PrayTen"  # 角色池十连
    ArmPray_One = "/api/ArmPray/PrayOne"  # 武器池单抽
    ArmPray_Ten = "/api/ArmPray/PrayTen"  # 武器池十连
    PermPray_One = "/api/PermPray/PrayOne"  # 常驻池单抽
    PermPray_Ten = "/api/PermPray/PrayTen"  # 常驻十连
    FullRolePray_One = "/api/FullRolePray/PrayOne"  # 全角色池单抽
    FullRolePray_Ten = "/api/FullRolePray/PrayTen"  # 全角色池十连
    FullArmPray_One = "/api/FullArmPray/PrayOne"  # 全武器池单抽
    FullArmPray_Ten = "/api/FullArmPray/PrayTen"  # 全武器池十连

    # 武器定轨
    SetMemberAssign = "/api/PrayInfo/SetMemberAssign"  # 武器定轨
    GetMemberAssign = "/api/PrayInfo/GetMemberAssign"  # 查询定轨

    # 查询
    GetPondInfo = "/api/PrayInfo/GetPondInfo"  # 查询蛋池
    GetMemberPrayDetail = "/api/PrayInfo/GetMemberPrayDetail"  # 查询成员祈愿信息
    GetMemberPrayRecords = "/api/PrayInfo/GetMemberPrayRecords"  # 查询成员祈愿记录
    GetLuckRanking = "/api/PrayInfo/GetLuckRanking"  # 获取欧气排行

    # 设置
    SetRolePond = "/api/PrayInfo/SetRolePond"  # 配置角色池
    SetArmPond = "/api/PrayInfo/SetArmPond"  # 配置武器池
    ResetRolePond = "/api/PrayInfo/ResetRolePond"  # 清空角色池
    ResetArmPond = "/api/PrayInfo/ResetArmPond"  # 清空武器池
    SetSkinRate = "/api/PrayInfo/SetSkinRate"  # 设定服装概率


class ResultCode(object):
    """
    响应码
    """
    code_str = {
        0: "成功",
        600: "未知错误",
        601: "Api每日调用次数达到上限",
        602: "参数无效",
        603: "找不到物品",
        604: "Api限制",
        605: "当前up池不在存在待定轨的物品",
        606: "卡池未配置",
        607: "权限不足",
        -1: "请求过程中出错",
        -2: "积分不足",
        404: "找不到指定的api地址"
    }
    code: int
    msg: str

    def __init__(self, code: int, msg: str = ""):
        """
        响应码
        :param code:响应码
        """
        self.code = code
        self.msg = msg

    def to_String(self):
        try:
            if self.msg and self.code != 0:
                return self.msg
            return self.code_str[self.code]
        except:
            self.code = -1
            return self.code_str[self.code]

    def is_success(self):
        if self.code == 0:
            return True
        return False


class Result(object):
    """
    结果
    code: 状态码
    data: 完整响应数据
    imgUrl: 图片路径
    message: 合成后的消息文本
    error: 错误信息
    source: 源数据
    """
    code: ResultCode
    data: dict
    imgUrl: str
    message: str
    error: str
    source: dict

    def __init__(self, code: ResultCode, data: dict, error: str = "", source: dict = {}):
        self.code = code
        self.data = data
        try:
            self.imgUrl = data["imgHttpUrl"]
        except:
            self.imgUrl = ""
        self.message = ""
        self.error = error
        self.source = source


class Request(object):
    """
    url: 请求地址
    headers: 请求头
    result: 响应内容
    param: 请求参数
    """
    url: str
    headers: dict
    result: Result
    param: dict

    def __init__(self, url: str, headers: dict, param: dict):
        """
        url: 请求地址
        headers: 请求头
        param: 参数
        """
        url = api_url + url
        self.url = url
        self.param = param
        headers.update({'content-type': 'application/json'})
        self.headers = headers

    def post_request(self):
        """
        POST请求
        """
        try:
            result = requests.post(url=self.url, headers=self.headers, data=json.dumps(self.param))
            if result.status_code == 200:
                js = result.json()
                data = js["data"]
                code = ResultCode(js["code"], js["message"])
                self.result = Result(code, data, source=result.json())
            else:
                data = {}
                code = ResultCode(result.status_code)
                self.result = Result(code, data, source=result.json())
        except Exception as e:
            self.result = Result(ResultCode(-1), {}, str(e))

    def get_request(self):
        """
        GET请求
        """
        try:
            url = "?"
            for p in self.param:
                url += f"{p}={self.param[p]}&"
            self.url += url.strip("&")
            result = requests.get(url=self.url, headers=self.headers)
            if result.status_code == 200:
                js = result.json()
                data = js["data"]
                code = ResultCode(js["code"], js["message"])
                self.result = Result(code, data)
            else:
                data = {}
                code = ResultCode(result.status_code)
                self.result = Result(code, data)
        except Exception as e:
            self.result = Result(ResultCode(-1), {}, str(e))

    def set_url(self, url: str):
        """
        修改URL,只需传入 CommandUrl 内的属性
        :param url: 接口地址
        """
        self.url = f"{api_url}{url}"


class Pray(object):
    """
    祈愿类
    request: 请求类
    """
    request: Request

    def __init__(
            self,
            url: str,
            authorzation: str,
            memberCode: str,
            memberName: str = "",
            pondIndex: int = 0,
            imgWidth: int = 1920,
            toBase64: bool = False
    ):
        """
        初始化
        :param url:请求地址
        :param authorzation:授权码,一般为群号
        :param memberCode:成员编号,一般为QQ号
        :param memberName:成员名称,一般为昵称
        :param pondIndex:蛋池编号,角色池可用
        :param imgWidth:图片宽度,单位px
        :param toBase64:是否返回Base64字符串
        """

        self.request = Request(
            url=url,
            headers={"authorzation": authorzation},
            param={
                "memberCode": memberCode,
                "memberName": memberName,
                "pondIndex": pondIndex,
                "imgWidth": imgWidth,
                "toBase64": toBase64
            }
        )

    def get_result(self):
        """
        获取祈愿结果
        """
        self.request.get_request()
        result = self.request.result
        return result


class Assign(object):
    """
    定轨类
    request: 请求类
    """
    request: Request

    def __init__(
            self,
            authorzation: str,
            memberCode: str,
            goodsName: str,
            memberName: str = ""
    ):
        """
        初始化
        :param authorzation:授权码,一般为群号
        :param memberCode:成员编号,一般为QQ号
        :param goodsName:武器名称
        :param memberName:成员名称,一般为昵称
        """
        self.request = Request(
            CommandUrl.SetMemberAssign,
            {"authorzation": authorzation},
            {
                "memberCode": memberCode,
                "memberName": memberName,
                "goodsName": goodsName
            }
        )

    def Set_Assign(self):
        """
        武器定轨
        返回定轨结果
        """
        self.request.get_request()
        return self.request.result


class Query(object):
    """
    查询类
    request: 请求类
    """
    request: Request

    def __init__(
            self,
            authorzation: str,
            memberCode: str = ""
    ):
        """
        初始化
        :param authorzation:授权码,一般为群号
        :param memberCode:成员编号,一般为QQ号,在部分查询中不需要
        """
        self.request = Request(
            "",
            {"authorzation": authorzation},
            {"memberCode": memberCode}
        )

    def Get_Assign(self):
        """
        查询定轨
        """
        self.request.set_url(CommandUrl.GetMemberAssign)
        self.request.get_request()
        return self.request.result

    def GetPondInfo(self):
        """
        查询蛋池列表
        """
        self.request.set_url(CommandUrl.GetPondInfo)
        self.request.get_request()
        return self.request.result

    def GetPrayDetail(self):
        """
        获取成员祈愿信息
        """
        self.request.set_url(CommandUrl.GetMemberPrayDetail)
        self.request.get_request()
        return self.request.result

    def GetPrayRecord(self):
        """
        获取成员祈愿记录
        """
        self.request.set_url(CommandUrl.GetMemberPrayRecords)
        self.request.get_request()
        return self.request.result

    def GetLuckRanking(self):
        """
        获取祈愿排行榜
        """
        self.request.set_url(CommandUrl.GetLuckRanking)
        self.request.get_request()
        return self.request.result


class Setting(object):
    """
    设置类
    request: 请求类
    """
    request: Request

    def __init__(
            self,
            authorzation: str,
            args: dict = {}
    ):
        """
        初始化
        :param authorzation:授权码,一般为群号
        :param args:参数
        """
        self.request = Request(
            "",
            {"authorzation": authorzation},
            args
        )

    def SetRolePond(self):
        """
        自定义角色池
        """
        self.request.set_url(CommandUrl.SetRolePond)
        self.request.post_request()
        return self.request.result

    def SetArmPond(self):
        """
        自定义角色池
        """
        self.request.set_url(CommandUrl.SetArmPond)
        self.request.post_request()
        return self.request.result

    def ResetRolePond(self):
        """
        清空角色池
        """
        self.request.set_url(CommandUrl.ResetRolePond)
        self.request.post_request()
        return self.request.result

    def ResetArmPond(self):
        """
        清空武器池
        """
        self.request.set_url(CommandUrl.ResetArmPond)
        self.request.post_request()
        return self.request.result

    def SetSkinRate(self):
        """
        设置角色服装出现概率
        """
        self.request.set_url(CommandUrl.SetSkinRate)
        self.request.post_request()
        return self.request.result
