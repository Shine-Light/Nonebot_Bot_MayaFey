import ujson as json
import os
import sys
from datetime import datetime

from httpx import AsyncClient
from nonebot.log import logger
from utils.path import *


# 写入与读取订阅信息
# method="w" 写入时返回新增订阅结果字符串
# method="r" 读取时返回订阅状态字典
async def subscribeHelper(method="r", subType="", subject=""):
  try:
    resPath = epicFree_path
    cache = epicFree_path / "status.json"
    assert os.path.exists(cache)
  except (AttributeError, AssertionError):
    resPath = os.path.dirname(os.path.abspath(__file__))
    cache = f"{resPath}{os.sep}status.json"
  try:
    with open(cache, "r", encoding="UTF-8") as f:
      statusDict = json.load(f)
  except FileNotFoundError:
    statusDict = {"群聊": [], "私聊": []}
    with open(cache, "w", encoding="UTF-8") as f:
      json.dump(statusDict, f, ensure_ascii=False, indent=2)
  except Exception as e:
    logger.error("获取 Epic 订阅 JSON 错误：" + str(sys.exc_info()[0]) + "\n" + str(e))
  # 读取时，返回订阅状态字典
  if method != "w":
    return statusDict
  # 写入时，将新的用户按类别写入至指定数组
  try:
    if subject in statusDict[subType]:
      return f"{subType}已经订阅过 Epic 限免游戏资讯了哦！"
    statusDict[subType].append(subject)
    with open(cache, "w", encoding="UTF-8") as f:
      json.dump(statusDict, f, ensure_ascii=False, indent=2)
      f.close()
    return f"{subType}订阅 Epic 限免游戏资讯成功！"
  except Exception as e:
    logger.error("获取 Epic 订阅 JSON 错误：" + str(sys.exc_info()[0]) + "\n" + str(e))
    return f"{subType}订阅 Epic 限免游戏资讯失败惹.."


# 获取所有 Epic Game Store 促销游戏
# 方法参考：RSSHub /epicgames 路由
# https://github.com/DIYgod/RSSHub/blob/master/lib/routes/epicgames/index.js
async def getEpicGame():
  epic_url = "https://www.epicgames.com/graphql"
  headers = {
    "Referer": "https://www.epicgames.com/store/zh-CN/",
    "Content-Type": "application/json; charset=utf-8",
  }
  data = {
    "query":
    "query searchStoreQuery($allowCountries: String, $category: String, $count: Int, $country: String!, $keywords: String, $locale: String, $namespace: String, $sortBy: String, $sortDir: String, $start: Int, $tag: String, $withPrice: Boolean = false, $withPromotions: Boolean = false) {\n Catalog {\n searchStore(allowCountries: $allowCountries, category: $category, count: $count, country: $country, keywords: $keywords, locale: $locale, namespace: $namespace, sortBy: $sortBy, sortDir: $sortDir, start: $start, tag: $tag) {\n elements {\n title\n id\n namespace\n description\n effectiveDate\n keyImages {\n type\n url\n }\n seller {\n id\n name\n }\n productSlug\n urlSlug\n url\n items {\n id\n namespace\n }\n customAttributes {\n key\n value\n }\n categories {\n path\n }\n price(country: $country) @include(if: $withPrice) {\n totalPrice {\n discountPrice\n originalPrice\n voucherDiscount\n discount\n currencyCode\n currencyInfo {\n decimals\n }\n fmtPrice(locale: $locale) {\n originalPrice\n discountPrice\n intermediatePrice\n }\n }\n lineOffers {\n appliedRules {\n id\n endDate\n discountSetting {\n discountType\n }\n }\n }\n }\n promotions(category: $category) @include(if: $withPromotions) {\n promotionalOffers {\n promotionalOffers {\n startDate\n endDate\n discountSetting {\n discountType\n discountPercentage\n }\n }\n }\n upcomingPromotionalOffers {\n promotionalOffers {\n startDate\n endDate\n discountSetting {\n discountType\n discountPercentage\n }\n }\n }\n }\n }\n paging {\n count\n total\n }\n }\n }\n}\n",
    "variables": {
      "allowCountries": "CN",
      "category": "freegames",
      "count": 1000,
      "country": "CN",
      "locale": "zh-CN",
      "sortBy": "effectiveDate",
      "sortDir": "asc",
      "withPrice": True,
      "withPromotions": True
    }
  }
  async with AsyncClient(proxies={"all://": None}) as client:
    try:
      res = await client.post(epic_url, headers=headers, json=data, timeout=10.0)
      resJson = res.json()
      games = resJson["data"]["Catalog"]["searchStore"]["elements"]
      return games
    except Exception as e:
      logger.error("请求 Epic Store API 错误：" + str(sys.exc_info()[0]) + "\n" + str(e))
      return None


# 获取 Epic Game Store 免费游戏信息
# 处理免费游戏的信息方法借鉴 pip 包 epicstore_api 示例	
# https://github.com/SD4RK/epicstore_api/blob/master/examples/free_games_example.py
async def getEpicFree():
  games = await getEpicGame()
  if not games:
    return "Epic 可能又抽风啦，请稍后再试（"
  else:
    for game in games:
      try:
        game_name = game["title"]
        game_corp = game["seller"]["name"]
        game_price = game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
        game_promotions = game["promotions"]
        if not game_promotions:
          continue    # 无促销，跳过
        else:
          upcoming_promotions = game["promotions"]["upcomingPromotionalOffers"]
          if upcoming_promotions:
            continue   # 促销即将上线，跳过
          per = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]['discountPercentage']
          if per is not 0:
            continue   # 非免费,跳过
          for image in game["keyImages"]:
            game_thumbnail = image["url"] if image["type"] == "Thumbnail" else None
          for pair in game["customAttributes"]:
            game_dev = pair["value"] if pair["key"] == "developerName" else game_corp
            game_pub = pair["value"] if pair["key"] == "publisherName" else game_corp
          game_desp = game["description"]
          end_date_iso = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"][:-1]
          end_date = datetime.fromisoformat(end_date_iso).strftime("%b.%d %H:%M")
          # API 返回不包含游戏商店 URL，此处自行拼接，可能出现少数游戏 404 请反馈
          msg = f"本周Epic喜加一\n"
          msg += f"[CQ:image,file={game_thumbnail}]\n\n" if game_thumbnail else ""
          msg += f"FREE now :: {game_name} ({game_price})\n\n{game_desp}\n\n"
          msg += f"游戏由 {game_pub} 发售，" if game_dev == game_pub else f"游戏由 {game_dev} 开发、{game_pub} 出版，"
          game_url = f"https://www.epicgames.com/store/zh-CN/p/{game['productSlug'].replace('/home', '')}"
          msg += f"将在 UTC 时间 {end_date} 结束免费游玩，戳链接领取吧~\n{game_url}"
      except (TypeError, IndexError, AttributeError):
        pass
      except Exception as e:
        logger.error("组织 Epic 订阅消息错误：" + str(sys.exc_info()[0]) + "\n" + str(e))
    # 返回整理为 CQ 码的消息字符串
    return msg
