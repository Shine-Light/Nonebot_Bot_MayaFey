from pathlib import Path

from nonebot_plugin_htmlrender import template_to_pic

from .weather_data import Weather


async def render(weather: Weather) -> bytes:
    template_path = str(Path(__file__).parent / "templates")

    return await template_to_pic(
        template_path=template_path,
        template_name="weather.html",
        templates={
            "now": weather.now["now"],
            "days": add_date(weather.daily["daily"]),
            "city": weather.city_name,
            "warning": weather.warning,
            "air": add_tag_color(weather.air["now"]) if "now" in weather.air else None,
        },
        pages={
            "viewport": {"width": 1000, "height": 300},
            "base_url": f"file://{template_path}",
        },
    )


def add_date(daily):
    from datetime import datetime

    week_map = [
        "周日",
        "周一",
        "周二",
        "周三",
        "周四",
        "周五",
        "周六",
    ]

    for day in range(len(daily)):
        date = daily[day]["fxDate"].split("-")
        _year = int(date[0])
        _month = int(date[1])
        _day = int(date[2])
        week = int(datetime(_year, _month, _day, 0, 0).strftime("%w"))
        daily[day]["week"] = week_map[week] if day != 0 else "今日"
        daily[day]["date"] = f"{_month}月{_day}日"

    return daily


def add_tag_color(air):
    color = {
        "优": "#95B359",
        "良": "#A9A538",
        "轻度污染": "#E0991D",
        "中度污染": "#D96161",
        "重度污染": "#A257D0",
        "严重污染": "#D94371",
    }
    air["tag_color"] = color[air["category"]]
    return air
