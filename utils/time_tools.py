"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/24 20:01
"""
import datetime

s2d: str = '%Y-%m-%d'


# 计算日期差距 -> 差距的天数
def date_calc(time_pre: str, time_next: str) -> int:
    date1: datetime = datetime.datetime.strptime(time_pre, s2d)
    date2: datetime = datetime.datetime.strptime(time_next, s2d)
    delta_day = (date2 - date1).days
    return delta_day

