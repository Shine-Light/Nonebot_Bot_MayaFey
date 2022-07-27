from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """百度翻译配置，见 https://fanyi-api.baidu.com/doc/21"""
    appid: str = ""
    salt: str = ""
    key: str = ""
