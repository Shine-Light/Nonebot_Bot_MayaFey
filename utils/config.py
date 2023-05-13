"""
@Author: Shine_Light
@Version: 1.0
@Date: 2023/1/3 16:52
"""
import ujson as json
from dataclasses import dataclass, field
from typing import Dict, Any, Union
from pathlib import Path
from nonebot.plugin import PluginMetadata, Plugin
from nonebot.log import logger
from .json_tools import json_load, json_update, json_write
from .path import config_path as global_config_path
from .other import mk_sync, translate_update, translate
from .const import GENERATE_TYPE_GROUP, GENERATE_TYPE_GENERAL, GENERATE_TYPE_NONE, GENERATE_TYPE_SINGLE
from .path import permission_common_base, permission_special_base, unset_path, total_unable, cd_path
from .permission import get_plugin_permission, get_special_per


def parse_configs(configs: Dict[str, Any], plugin_name: str, gid: str = None) -> Dict[Union[str, Path], Union[str, dict]]:
    """
    解析configs
    configs: configs对象
    plugin_name: 插件名
    gid: 群号,用于群号替换
    """
    result = {}
    for key in configs:
        value = configs[key]
        if isinstance(value, dict):
            if gid:
                key = key.replace("{{gid}}", gid)
            config_path = global_config_path / plugin_name / key
            value_dict = {}
            for key2 in value:
                value_dict.update({key2: value[key2]})
            result.update({config_path: value_dict})
        elif isinstance(key, str):
            result.update({key: value})
    return result


@dataclass
class PluginConfig(object):
    """
    plugin_name: 插件名
    plugin_meta: 插件元数据
        name: 插件名,默认为模块名
        description: 插件简介
        usage: 使用方法
        extra: 附加属性
            generate_type: 配置生成类型
                group: 配置分群管理
                single: 配置不分群
                general: 只生成通用配置
                none: 不生成配置,默认类型
            permission_common: 插件正常模式权限,默认 member
            unset: 是否为不可控制插件,默认 False
            total_unable: 是否为不统计插件,默认 False
            version: 插件版本
            author: 插件作者
            translate: 插件名称中文
            permission_special: 插件特殊模式权限
                {matcher名称: 权限}
            cd: 插件cd配置
                {
                    plugin: {count: 次数(默认5), time: 时间(默认10s), ban_time: 禁言时间(默认300s)},
                    matcher: {
                        matcher名称: 同plugin配置
                    }
                }
            configs: 插件配置
                {配置名称: 值} 默认为存储在config.json
                {配置文件路径: {
                        配置名称: 值,
                        配置名称: 值...
                }}
                配置实际路径为 config/插件名/配置文件路径 可用 {{gid}} 表示群号,非group类型插件无效
            configs_general: 插件通用配置,即不会分群
                {配置名称: 值}
    """
    plugin_name: str

    plugin_meta: PluginMetadata = None
    description: str = field(default_factory=str)
    usage: str = field(default_factory=str)
    generate_type: bool = field(default="none")
    permission_common: str = field(default="member")
    unset: bool = field(default=False)
    total_unable: bool = field(default=False)
    version: str = field(default_factory=str)
    author: str = field(default_factory=str)
    permission_special: dict = field(default_factory=dict)
    translate: str = field(default_factory=str)
    cd: dict = field(default_factory=dict)
    configs: Dict[str, Any] = field(default_factory=dict)
    configs_general: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        初始化配置
        """
        # 属性初始化
        if not self.plugin_meta:
            self.plugin_meta = PluginMetadata(self.plugin_name, "", "")
            logger.debug(f"无法读取插件 {self.plugin_name} 的 PluginMetadata,使用默认配置")
        else:
            if self.plugin_meta.description:
                self.description = self.plugin_meta.description
            if self.plugin_meta.usage:
                self.usage = self.plugin_meta.usage
            if "generate_type" in self.plugin_meta.extra:
                self.generate_type = self.plugin_meta.extra['generate_type']
            if "permission_common" in self.plugin_meta.extra:
                self.permission_common = self.plugin_meta.extra['permission_common']
            if "unset" in self.plugin_meta.extra:
                self.unset = self.plugin_meta.extra['unset']
            if "total_unable" in self.plugin_meta.extra:
                self.total_unable = self.plugin_meta.extra['total_unable']
            if "version" in self.plugin_meta.extra:
                self.version = self.plugin_meta.extra['version']
            if "author" in self.plugin_meta.extra:
                self.author = self.plugin_meta.extra['author']
            if "permission_special" in self.plugin_meta.extra:
                self.permission_special = self.plugin_meta.extra['permission_special']
            if "translate" in self.plugin_meta.extra:
                self.translate = self.plugin_meta.extra['translate']
            if "cd" in self.plugin_meta.extra:
                self.cd = self.plugin_meta.extra['cd']
            if "configs" in self.plugin_meta.extra:
                self.configs = self.plugin_meta.extra['configs']
            if "configs_general" in self.plugin_meta.extra:
                self.configs_general = self.plugin_meta.extra['configs_general']
        # 名称翻译初始化
        if not self.translate:
            self.translate = self.plugin_meta.name
        # 不覆盖已存在的翻译
        if translate("e2c", self.plugin_name) == self.plugin_name:
            translate_update(self.plugin_meta.name, self.translate)
        self.plugin_meta.name = self.translate
        # 不可控制配置初始化
        if self.unset:
            if self.plugin_name not in open(unset_path, "r", encoding="utf-8").read():
                with open(unset_path, "a", encoding="utf-8") as file:
                    file.write(f",{self.plugin_name}")
        # 不统计配置初始化
        if self.total_unable:
            if self.plugin_name not in open(total_unable, "r", encoding="utf-8").read():
                with open(total_unable, "a", encoding="utf-8") as file:
                    file.write(f",{self.plugin_name}")
        # 配置文件初始化
        self.__config_path__ = global_config_path / self.plugin_name
        self.__config_general_path__ = global_config_path / self.plugin_name / "config_general.json"
        # 不配置类型
        if self.generate_type == GENERATE_TYPE_NONE:
            return
        # 通用配置初始化,不覆盖已有配置,但允许新增配置
        if self.generate_type in [GENERATE_TYPE_GENERAL, GENERATE_TYPE_GROUP, GENERATE_TYPE_SINGLE]:
            if not self.__config_path__.exists():
                mk_sync("dir", self.__config_path__)
            if not self.__config_general_path__.exists():
                mk_sync("file", self.__config_general_path__, "w", content=json.dumps(self.configs_general))
            for key in self.configs_general:
                if key not in json_load(self.__config_general_path__):
                    json_update(self.__config_general_path__, key, self.configs_general[key])
        # 不分群配置可以即刻初始化,不覆盖已有配置,但允许新增配置
        if self.generate_type == GENERATE_TYPE_SINGLE:
            configs = parse_configs(self.configs, self.plugin_name)
            self.__config_default_path__ = self.__config_path__ / "config.json"
            if not self.__config_default_path__.exists():
                mk_sync("file", self.__config_default_path__, "w", content=json.dumps({}))
            for key in configs:
                if isinstance(key, Path):
                    if not key.parent.exists():
                        key.parent.mkdir(parents=True, exist_ok=True)
                    if not key.exists():
                        mk_sync("file", key, "w", content=json.dumps({}))
                    for key1 in configs[key]:
                        if key1 not in json_load(key):
                            json_update(key, key1, configs[key][key1])
                else:
                    if key not in json_load(self.__config_default_path__):
                        json_update(self.__config_default_path__, key, configs[key])

    def init(self, gid: str):
        # 权限初始化,不覆盖已存在的权限
        if not get_plugin_permission(gid, self.plugin_name):
            json_update(permission_common_base / f"{gid}.json", self.plugin_name, self.permission_common)
        if self.permission_special:
            for matcher in self.permission_special:
                if not get_special_per(gid, matcher):
                    json_update(permission_special_base / f"{gid}.json", matcher, self.permission_special.get(matcher))

        # cd配置初始化,不覆盖已存在的配置
        if not (cd_path / gid).exists():
            (cd_path / gid).mkdir(exist_ok=True, parents=True)
            mk_sync("file", cd_path / gid / "cd.json", "w", content=json.dumps({self.plugin_name: self.cd}))
        if not (cd_path / gid / "cd.json").exists():
            mk_sync("file", cd_path / gid / "cd.json", "w", content=json.dumps({self.plugin_name: self.cd}))
        conf_source: dict = json_load(cd_path / gid / "cd.json").get(self.plugin_name)
        if not conf_source:
            if self.cd:
                conf_source = self.cd
            else:
                conf_source = {
                    "plugin": {
                        "count": 5,
                        "time": 10,
                        "ban_time": 300
                    },
                    "matcher": {}
                }
        if len(self.cd) != 0 and not self.cd.get("plugin") and not conf_source.get("plugin"):
            conf_source = ({"plugin": self.cd, "matcher": {}})
        if self.cd.get("matcher"):
            if conf_source.get("matcher"):
                for name, conf in self.cd.get("matcher").items():
                    if name not in conf_source.get("matcher"):
                        conf_source.get("matcher").update({name: conf})
            else:
                conf_source.update({"matcher": self.cd.get("matcher")})
        if len(self.cd) == 0 and not conf_source:
            conf_source.update({"plugin": {"count": 0, "time": 0, "ban_time": 0}, "matcher": {}})
        if conf_source.get("plugin").get("time") is None:
            conf_source.get("plugin").update({"time": 10})
        if conf_source.get("plugin").get("count") is None:
            conf_source.get("plugin").update({"count": 5})
        if conf_source.get("plugin").get("ban_time") is None:
            conf_source.get("plugin").update({"ban_time": 300})
        for name, conf in conf_source.get("matcher").items():
            if conf.get("time") is None:
                conf.update({"time": 10})
            if conf.get("count") is None:
                conf.update({"count": 5})
            if conf.get("ban_time") is None:
                conf.update({"ban_time": 300})
        json_update(cd_path / gid / "cd.json", self.plugin_name, conf_source)

    def init_config(self, gid: str):
        # 配置初始化,不覆盖已有配置,但允许新增配置
        configs = parse_configs(self.configs, self.plugin_name, gid)
        config_default_path = self.__config_path__ / gid / "config.json"
        for key in configs:
            # 自定义路径配置
            if isinstance(key, Path):
                if not key.parent.exists():
                    key.parent.mkdir(parents=True, exist_ok=True)
                if not key.exists():
                    mk_sync("file", key, "w", content=json.dumps({}))
                for key1 in configs[key]:
                    if key1 not in json_load(key):
                        json_update(key, key1, configs[key][key1])
            # 默认路径配置
            else:
                if not config_default_path.parent.exists():
                    config_default_path.parent.mkdir(parents=True, exist_ok=True)
                if not config_default_path.exists():
                    mk_sync("file", config_default_path, "w", content=json.dumps({}))
                    json_update(config_default_path, key, configs[key])
                else:
                    if key not in json_load(config_default_path):
                        json_update(config_default_path, key, configs[key])

    def get_config(self, config_name: str, gid: str = None, config_path: str = None) -> Any:
        """
        获取配置,没有该配置时返回None
        群聊插件默认使用 config/插件/群号/config.json
        非群聊插件默认使用 config/插件/config.json
        config_name: 配置名称
        gid: 群号,生成类型为群聊时需要
        config_path: 配置路径,可用{{gid}}表示群号,可选
        """
        try:
            if self.generate_type == GENERATE_TYPE_NONE or self.generate_type == GENERATE_TYPE_GENERAL:
                logger.warning(f"[{self.plugin_name}] 不生成配置和通用配置插件无法获取自定义配置")
                return
            elif self.generate_type == GENERATE_TYPE_GROUP:
                if not gid:
                    logger.warning(f"[{self.plugin_name}] 群聊插件获取自定义配置缺少群号")
                if config_path:
                    if self.generate_type == GENERATE_TYPE_GROUP and gid:
                        config_path = config_path.replace("{{gid}}", gid)
                    return json_load(global_config_path / self.plugin_name / config_path)[config_name]
                else:
                    config_default_path = self.__config_path__ / gid / "config.json"
                    return json_load(config_default_path)[config_name]
            else:
                if config_path:
                    return json_load(global_config_path / self.plugin_name / config_path)[config_name]
                else:
                    config_default_path = self.__config_path__ / "config.json"
                    return json_load(config_default_path)[config_name]
        except KeyError:
            logger.error(f"[{self.plugin_name}] 不存在 {config_name} 配置项")
            return None
        except FileNotFoundError:
            logger.error(f"[{self.plugin_name}] 找不到 {config_path} 文件")

    def set_config(self, config_name: str, config_value, gid: str = None, config_path: str = None):
        """
        修改配置
        config_name: 配置名称
        config_value: 配置值
        gid: 群号,生成类型为群聊时需要
        config_path: 配置路径,可用{{gid}}表示群号,可选
        """
        try:
            if self.generate_type == GENERATE_TYPE_NONE or self.generate_type == GENERATE_TYPE_GENERAL:
                logger.warning(f"[{self.plugin_name}] 不生成配置和通用配置插件无法修改自定义配置")
                return
            elif self.generate_type == GENERATE_TYPE_GROUP:
                if not gid:
                    logger.warning(f"[{self.plugin_name}] 群聊插件修改自定义配置缺少群号")
                    return
                if config_path:
                    if self.generate_type == GENERATE_TYPE_GROUP and gid:
                        config_path = config_path.replace("{{gid}}", gid)
                    json_update(global_config_path / self.plugin_name / config_path, config_name, config_value)
                else:
                    config_default_path = self.__config_path__ / gid / "config.json"
                    json_update(config_default_path, config_name, config_value)
            else:
                if config_path:
                    json_update(global_config_path / self.plugin_name / config_path, config_name, config_value)
                else:
                    config_default_path = self.__config_path__ / "config.json"
                    json_update(config_default_path, config_name, config_value)
        except FileNotFoundError:
            logger.error(f"[{self.plugin_name}] 找不到 {config_path} 文件")

    def add_config(self, gid: str = None, config_path: str = None):
        """
        新增配置文件,若文件已存在则跳过
        gid: 群号,用{{gid}}表示群号时需要,生成类型不为群聊时无效
        config_path: 配置路径,可用{{gid}}表示群号
        """
        if gid and self.generate_type == GENERATE_TYPE_GROUP:
            config_path = config_path.replace("{{gid}}", gid)
        if (global_config_path / self.plugin_name / config_path).exists():
            logger.warning(f"[{self.plugin_name}] {config_path} 配置文件已存在,不再创建")
        else:
            json_write(global_config_path / self.plugin_name / config_path, {})
            logger.debug(f"[{self.plugin_name}] 创建配置文件 {config_path}")

    def get_config_general(self, config_name: str) -> Any:
        """
        获取通用配置,没有该配置时返回None
        config_name: 配置名称
        """
        try:
            if self.generate_type == GENERATE_TYPE_NONE:
                logger.warning(f"[{self.plugin_name}] 未生成配置插件无法获取通用配置")
                return
            return json_load(self.__config_general_path__)[config_name]
        except KeyError:
            logger.error(f"[{self.plugin_name}] 无法读取 {config_name} 通用配置项")
            return None

    def set_config_general(self, config_name: str, config_value):
        """
        修改通用配置
        config_name: 配置名称
        config_value: 配置值
        """
        if self.generate_type == GENERATE_TYPE_NONE:
            logger.warning(f"[{self.plugin_name}] 未生成配置插件无法修改通用配置")
            return
        json_update(self.__config_general_path__, config_name, config_value)

    def dict(self) -> dict:
        return {
            "plugin_meta": self.plugin_meta,
            "description": self.description,
            "usage":self.usage,
            "generate_type": self.generate_type,
            "permission_common": self.permission_common,
            "unset": self.unset,
            "total_unable":self.total_unable,
            "version": self.version,
            "author": self.author,
            "permission_special": self.permission_special,
            "translate":  self.translate,
            "cd": self.cd,
        }


@dataclass
class ConfigManager(object):
    __configs__: Dict[str, PluginConfig] = field(default_factory=dict)

    def initAllPlugin(self, gid: str):
        """
        初始化所有插件配置
        """
        for pluginConfig in self.__configs__.values():
            pluginConfig.init(gid)
            if pluginConfig.generate_type == GENERATE_TYPE_GROUP:
                self.initGroupPlugin(pluginConfig.plugin_name, gid)

    def addPluginConfig(self, plugin: Plugin):
        """
        添加插件配置
        plugin: Plugin对象
        """
        metadata = plugin.metadata
        try:
            if not metadata and plugin.module.meta:
                metadata = plugin.module.meta
        except AttributeError:
            pass
        plugin_config = PluginConfig(plugin.name, metadata)
        self.__configs__.update({plugin.name: plugin_config})

    def getPluginConfig(self, plugin_name: str):
        """
        获取插件配置,没有该插件配置时返回None
        plugin_name: 插件名
        """
        return self.__configs__[plugin_name]

    def initGroupPlugin(self, plugin: str, gid: str):
        """
        初始化群聊插件配置
        plugin: Plugin对象
        gid: 群号
        """
        pluginConfig = self.getPluginConfig(plugin)
        pluginConfig.init_config(gid)

    def pluginConfigs(self):
        """
        获取已加载的插件的配置
        """
        return self.__configs__


manager = ConfigManager()
