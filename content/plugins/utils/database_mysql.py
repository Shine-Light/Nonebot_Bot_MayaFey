"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/23 12:47
"""

from nonebot import get_driver, require
import pymysql



host = get_driver().config.mysql_host
port = get_driver().config.mysql_port
user = get_driver().config.mysql_user
password = get_driver().config.mysql_password
database = get_driver().config.mysql_db

connect = pymysql.connect(host=host, user=user, passwd=password, db=database, autocommit=True)
cursor = connect.cursor()

scheduler = require("nonebot_plugin_apscheduler").scheduler
timezone = "Asia/Shanghai"
@scheduler.scheduled_job("cron", hour=6, timezone=timezone)
async def _():
    cursor.execute(f"USE {database}")
