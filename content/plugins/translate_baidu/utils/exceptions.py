"""
这里定义一些百度翻译返回的异常类型
API 参考：https://fanyi-api.baidu.com/doc/21
"""


class BaiduBaseException(Exception):
    """基类，代码 52000 是成功代码"""
    def __init__(self, code: str = "52000", msg: str = f"发生未知错误..."):
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"错误代码：{self.code}\t错误信息：{self.msg}"


class BaiduTimeoutException(BaiduBaseException):
    """请求超时"""
    def __init__(self, code: str = "52001", msg: str = "请求超时，请重试 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduInternalError(BaiduBaseException):
    """系统错误"""
    def __init__(self, code: str = "52002", msg: str = "系统错误，请重试 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduUnauthorizeException(BaiduBaseException):
    """未授权用户"""
    def __init__(self, code: str = "52003", msg: str = "请检查 appid 是否正确或者服务是否开通 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduMissingArgException(BaiduBaseException):
    """缺少必填参数"""
    def __init__(self, code: str = "54000", msg: str = "请检查是否少传参数 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduSignError(BaiduBaseException):
    """签名错误"""
    def __init__(self, code: str = "54001", msg: str = "请检查您的签名生成方法 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduFrequencyLimitException(BaiduBaseException):
    """访问频率受限"""
    def __init__(self, code: str = "54003", msg: str = "请降低您的调用频率，或进行身份认证后切换为高级版/尊享版 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduNoBalanceException(BaiduBaseException):
    """账户余额不足"""
    def __init__(self, code: str = "54004", msg: str = "请前往 https://api.fanyi.baidu.com/api/trans/product/desktop 为账户充值 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduLongQueryException(BaiduBaseException):
    """长 query 请求频繁"""
    def __init__(self, code: str = "54005", msg: str = "请降低长query的发送频率，3s后再试 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduIllegalClientIPException(BaiduBaseException):
    """客户端IP非法"""
    def __init__(self, code: str = "58000", msg: str = "检查个人资料里填写的IP地址是否正确，可前往 https://api.fanyi.baidu.com/access/0/3 修改 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduNotSupportLanguageException(BaiduBaseException):
    """译文语言方向不支持"""
    def __init__(self, code: str = "58001", msg: str = "检查译文语言是否在语言列表里 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduServiceClosedException(BaiduBaseException):
    """服务当前已关闭"""
    def __init__(self, code: str = "58002", msg: str = "请前往 https://api.fanyi.baidu.com/choose 开启服务 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class BaiduServiceUnavailableException(BaiduBaseException):
    """认证未通过或未生效"""
    def __init__(self, code: str = "90107", msg: str = "请前往 https://api.fanyi.baidu.com/myIdentify 开启服务 ..."):
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


EXCEPTIONS = {
    "52000": BaiduBaseException,
    "52001": BaiduTimeoutException,
    "52002": BaiduInternalError,
    "52003": BaiduUnauthorizeException,
    "54000": BaiduMissingArgException,
    "54001": BaiduSignError,
    "54003": BaiduFrequencyLimitException,
    "54004": BaiduNoBalanceException,
    "54005": BaiduLongQueryException,
    "58000": BaiduIllegalClientIPException,
    "58001": BaiduNotSupportLanguageException,
    "58002": BaiduServiceClosedException,
    "90107": BaiduServiceUnavailableException,
}
