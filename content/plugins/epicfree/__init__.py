import sys

from nonebot import on_regex, require, get_driver, get_bot
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (Bot, Event, GroupMessageEvent,
                                           Message, MessageEvent)

from .data_source import getEpicFree, subscribeHelper
from ..permission.tools import permission_
from utils import users

try:
  epicScheduler = get_driver().config.epic_scheduler
  assert epicScheduler is not None
except (AttributeError, AssertionError):
  epicScheduler = "5 8 8 8"
day_of_week, hour, minute, second = epicScheduler.split(" ")


epicMatcher = on_regex("((E|e)(P|p)(I|i)(C|c))?喜(加一|\+1)", priority=8)
@epicMatcher.handle()
async def onceHandle(bot: Bot, event: Event):
  imfree = await getEpicFree()
  await epicMatcher.finish(Message(imfree))


epicSubMatcher = on_regex("喜(加一|\+1)订阅", priority=7)
@epicSubMatcher.handle()
async def subHandle(bot: Bot, event: MessageEvent, state: T_State):
  gid = str(event.group_id)
  uid = str(event.user_id)
  if isinstance(event, GroupMessageEvent):
    if permission_(users.get_role(gid, uid), "superuser"):
      state["targetId"] = gid
      state["subType"] = "群聊"
      msg = await subscribeHelper("w", state["subType"], state["targetId"])
      await epicSubMatcher.finish(msg)


scheduler = require("nonebot_plugin_apscheduler").scheduler
@scheduler.scheduled_job("cron", day_of_week=day_of_week, hour=hour, minute=minute, second=second)
async def weeklyEpic():
  bot = get_bot()
  whoSubscribe = await subscribeHelper()
  imfree = await getEpicFree()
  try:
    for group in whoSubscribe["群聊"]:
        await bot.send_group_msg(group_id=group, message=Message(imfree))
    for private in whoSubscribe["私聊"]:
      await bot.send_private_msg(user_id=private, message=Message(imfree))
  except FinishedException:
    pass
  except Exception as e:
    logger.error("Epic 限免游戏资讯定时任务出错：" + str(sys.exc_info()[0]) + "\n" + str(e))
