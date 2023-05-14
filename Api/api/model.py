from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import Any, Optional

class Code():
    code: dict = {
        0: "成功",
        101: "接口错误",
        102: "参数错误",
        -1: "未知异常"
    }

@dataclass()
class Result(object):
    code: int = field(default=0)
    msg: str = field(default="成功")
    data: dict = field(default_factory=dict)
    code_msg: str = field(default="")

    def __post_init__(self):
        self.code_msg = Code.code.get(self.code) or "未知状态码"

    def dict(self) -> dict:
        return {
            "code": self.code,
            "msg": self.msg,
            "code_msg": self.code_msg,
            "data": self.data
        }

class LoginForm(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

class Group(BaseModel):
    group_id: str

class User(BaseModel):
    user_id: str
    role: Optional[str]
    credit: Optional[int]
    ban_count: Optional[int]
    sign_date_last: Optional[str]
    sign_count_all: Optional[int]
    sign_count_continue: Optional[int]

class Plugin(BaseModel):
    plugin_name: str
    enable: Optional[bool]
    total_unable: Optional[bool]
    permission: Optional[dict]
    cd: Optional[dict]

class Data(BaseModel):
    def __init__(self, **data: dict) -> None:
        super().__init__(**data)
        self.__dict__ = data

    def __getattr__(self, __name: str) -> Any:
        try:
            return self.__dict__[__name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, __name, __value):
        if __name == "__dict__":
            object.__setattr__(self, "__dict__", __value)
        else:
            self.__dict__.update({__name: __value})
