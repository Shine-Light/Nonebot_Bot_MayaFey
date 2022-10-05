"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/10/1 13:34
"""
import requests
from .config import Config

api_url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined"
content_type = "application/x-www-form-urlencoded"
config = Config()

type0 = {
        0: "百度官方违禁图"
    }
type1 = {
    0: "一般色情",
    1: "卡通色情",
    2: "SM",
    3: "低俗",
    4: "儿童裸露",
    5: "艺术品色情",
    6: "性玩具",
    7: "男性性感",
    8: "自然男性裸露",
    9: "女性性感",
    10: "卡通女性性感",
    11: "特殊类",
    12: "亲密行为",
    13: "卡通亲密行为",
    14: "孕肚裸露",
    15: "臀部特写",
    16: "脚部特写",
    17: "裆部特写"
}
type3 = {
    0: "恶心图",
    1: "性器官特写",
    2: "脏器",
    3: "疾病表症",
    4: "密集恐惧症",
    5: "腐烂食物",
    6: "排泄物",
    7: "恶心动物",
    8: "人体血腥和尸体",
    9: "动物血腥及尸体"
}
type7 = {
    0: "用户自定义图像黑名单"
}
type11 = {
    0: "百度默认违禁词库"
}
type12 = {
    0: "低质灌水",
    2: "文本色情",
    4: "恶意推广",
    5: "低俗辱骂",
    6: "恶意推广-联系方式",
    7: "恶意推广-软文推广",
    8: "广告法审核"
}
type21 = {
    1: "真人吸烟",
    2: "卡通吸烟",
    3: "毒品",
    4: "真人饮酒",
    5: "卡通饮酒",
    6: "赌博",
    7: "纹身",
    9: "竖中指",
    10: "野生动物制品"
}
types = {
    0: type0,
    1: type1,
    3: type3,
    7: type7,
    11: type11,
    12: type12,
    21: type21
}


class IllegalType(object):
    subType: str

    def __init__(self, mainType, subType):
        self.subType = types[mainType][subType]

    def __str__(self):
        return self.subType


class Result(object):
    illegal_level: int
    illegal_type: IllegalType = None
    error: str = None

    def __init__(self, res: dict = {}, error: int = 0):
        if error:
            self.error = "请求过程中出错,状态码:" + str(error)
        elif "error_code" in res:
            self.error = res['error_msg']
        else:
            self.illegal_level = res['conclusionType']
            if self.illegal_level > 1:
                data = res['data'][0]
                self.illegal_type = IllegalType(data['type'], data['subType'])

    def is_illegal(self):
        if (config.check_level == 1 and self.illegal_level in [2, 3]) or \
                (config.check_level == 0 and self.illegal_level == 2):
            return True
        else:
            return False

    def is_error(self):
        if self.error:
            return True
        else:
            return False


class Reqeust(object):
    image_base64: str
    imgUrl: str
    imgType: int

    def __init__(self, image_base64=None, imgUrl=None, imgType=0):
        self.image_base64 = image_base64
        self.imgUrl = imgUrl
        self.imgType = imgType

    def get_access_token(self):
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={config.access_key_baidu}&client_secret={config.access_secret_baidu}"
        re = requests.post(token_url)
        if re.status_code == 200:
            js = re.json()
            if "error" in js:
                return None
            else:
                return js['access_token']
        else:
            return None

    def request(self):
        access_token = self.get_access_token()
        if not access_token:
            result = Result(error=1)
            result.error = "无法获取密钥,secret或key错误"
            return result
        if self.image_base64:
            data = {
                "access_token": access_token,
                "Content-Type": content_type,
                "image": self.image_base64,
                "imgType": self.imgType
            }
        else:
            data = {
                "access_token": access_token,
                "Content-Type": content_type,
                "imgUrl": self.imgUrl,
                "imgType": self.imgType
            }
        re = requests.post(url=api_url, data=data)
        if re.status_code == 200:
            return Result(re.json())
        else:
            return Result(error=re.status_code)
