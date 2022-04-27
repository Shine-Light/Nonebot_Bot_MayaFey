from httpx import AsyncClient, Response
from nonebot.log import logger
from typing import Union
import asyncio


class APIError(Exception):
    ...


class ConfigError(Exception):
    ...


class CityNotFoundError(Exception):
    ...


class Weather:
    def __url__(self):
        if self.api_type == 2:
            self.url_weather_api = "https://api.qweather.com/v7/weather/"
            self.url_geoapi = "https://geoapi.qweather.com/v2/city/"
            self.url_weather_warning = "https://api.qweather.com/v7/warning/now"
            self.url_air = "https://api.qweather.com/v7/air/now"
            self.forecast_days = 7
            logger.info("使用商业版API")
        elif self.api_type == 0 or self.api_type == 1:
            self.url_weather_api = "https://devapi.qweather.com/v7/weather/"
            self.url_geoapi = "https://geoapi.qweather.com/v2/city/"
            self.url_weather_warning = "https://devapi.qweather.com/v7/warning/now"
            self.url_air = "https://devapi.qweather.com/v7/air/now"
            if self.api_type == 0:
                self.forecast_days = 3
                logger.info("使用普通版API")
            elif self.api_type == 1:
                self.forecast_days = 7
                logger.info("使用个人开发版API")
        else:
            raise ConfigError(
                "api_type 必须是为 (int)0 -> 普通版, (int)1 -> 个人开发版, (int)2 -> 商业版"
                f"\n当前为: ({type(self.api_type)}){self.api_type}"
            )

    def __init__(self, city_name: str, api_key: str, api_type: int = 0):
        self.city_name = city_name
        self.apikey = api_key
        self.api_type = api_type
        self.__url__()

        self.now = None
        self.daily = None
        self.air = None
        self.warning = None
        self.__reference = "\n请参考: https://dev.qweather.com/docs/start/status-code/"

    async def load_data(self):
        self.city_id = await self._get_city_id()
        self.now, self.daily, self.air, self.warning = await asyncio.gather(
            self._now, self._daily, self._air, self._warning
        )
        self._data_validate()

    async def _get_data(self, url: str, params: dict) -> Response:
        async with AsyncClient() as client:
            res = await client.get(url, params=params)
        return res

    async def _get_city_id(self, api_type: str = "lookup"):
        res = await self._get_data(
            url=self.url_geoapi + api_type,
            params={"location": self.city_name, "key": self.apikey},
        )

        res = res.json()
        logger.debug(res)
        if res["code"] == "404":
            raise CityNotFoundError()
        elif res["code"] != "200":
            raise APIError("错误! 错误代码: {}".format(res["code"]) + self.__reference)
        else:
            return res["location"][0]["id"]

    def _data_validate(self):
        if (
            self.now["code"] == "200"
            and self.daily["code"] == "200"
            and self.air["code"] in ["200", "403"]
        ):
            ...
        else:
            raise APIError(
                "错误! 请检查配置! "
                f'错误代码: now: {self.now["code"]}  '
                f'daily: {self.daily["code"]}  '
                f'air: {self.air["code"]}  '
                "warning: {}".format(
                    self.warning["code"] if not self.warning else "None"
                )
                + self.__reference
            )

    def _check_response(self, response: Response) -> bool:
        if response.status_code == 200:
            logger.debug(f"{response.json()}")
            return True
        else:
            raise APIError(f"Response code:{response.status_code}")

    @property
    async def _now(self) -> dict:
        res = await self._get_data(
            url=self.url_weather_api + "now",
            params={"location": self.city_id, "key": self.apikey},
        )
        self._check_response(res)
        return res.json()

    @property
    async def _daily(self) -> dict:
        res = await self._get_data(
            url=self.url_weather_api + str(self.forecast_days) + "d",
            params={"location": self.city_id, "key": self.apikey},
        )
        self._check_response(res)
        return res.json()

    @property
    async def _air(self) -> dict:
        res = await self._get_data(
            url=self.url_air,
            params={"location": self.city_id, "key": self.apikey},
        )
        self._check_response(res)
        return res.json()

    @property
    async def _warning(self) -> Union[dict, None]:
        res = await self._get_data(
            url=self.url_weather_warning,
            params={"location": self.city_id, "key": self.apikey},
        )
        self._check_response(res)
        return res.json()
