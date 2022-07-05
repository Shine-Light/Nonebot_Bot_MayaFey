"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/6/27 21:02
"""
from utils import path, json_tools
from typing import List


option = {"limit": "提醒阈值"}
option_type = {"limit": "int"}


def get_count(gid: str, uid: str) -> int:
    try:
        data = json_tools.json_load(path.demerit_path / gid / "data.json")
        return data[uid]["count"]
    except KeyError:
        return 0


def get_comments(gid: str, uid: str) -> List[str]:
    try:
        data = json_tools.json_load(path.demerit_path / gid / "data.json")
        m = data[uid]["comments"]
        return m
    except KeyError:
        return []


def add_demerit(gid: str, uid: str, note: str):
    data = json_tools.json_load(path.demerit_path / gid / "data.json")
    try:
        count: int = data[uid]["count"]
        count += 1
        comments: list = data[uid]["comments"]
        comments.append(note)
        data.update({uid: {"count": count, "comments": comments}})
    except KeyError:
        count = 1
        comments = [note]
        uid_data = {"count": count, "comments": comments}
        data.update({uid: uid_data})
    json_tools.json_write(path.demerit_path / gid / "data.json", data)


def get_limit(gid: str) -> int:
    config = json_tools.json_load(path.demerit_path / gid / "config.json")
    return config["limit"]


def get_config(gid: str) -> str:
    configs = json_tools.json_load(path.demerit_path / gid / "config.json")
    msg = "记过配置\n"
    for config in configs:
        try:
            msg += f"{option[config]}: {configs[config]}\n"
        except:
            pass
    return msg.strip("\n")


def set_config(gid: str, cfg: str, value: str) -> str:
    try:
        # 没有此配置
        if (cfg not in option) and (cfg not in option.values()):
            return "出错啦:没有这个配置!"
        else:
            # 中文转英文
            try:
                for n in option:
                    if cfg == option[n]:
                        cfg = n
                        break
            # 英文不操作
            except KeyError:
                pass
    except:
        return "出错啦:没有这个配置!"

    configs = json_tools.json_load(path.demerit_path / gid / "config.json")
    try:
        if cfg == "limit":
            value = int(value)
            configs[cfg] = value
    except:
        return "出错啦:这不是我要的类型!"

    json_tools.json_write(path.demerit_path / gid / "config.json", configs)
    return "设置成功!"
