from re import findall, sub
from typing import Tuple

from nonebot import get_driver
from nonebot.log import logger
from nonebot.plugin import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment

from .__utils__ import fetchInitRes, uidHelper
from .data_source import getPanelMsg
from nonebot.plugin import PluginMetadata
from utils.other import add_target, translate

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name=translate("e2c", "menu"),
    description="展示原神游戏内角色展柜数据",
    usage="/原神面板绑定 {uid}\n"
          "/原神面板"
          "/原神面板{uid}"
          "/原神面板 {角色}"
          "/原神面板@xx\n\n\n" + add_target(60)
)

driver = get_driver()
showPanel = on_command("panel", aliases={"原神评分", "原神面板"}, priority=7)


async def formatInput(msg: str, qq: str, atqq: str = "") -> Tuple[str, str]:
    """
    输入消息中的 UID 与角色名格式化，应具备处理 ``msg`` 为空、包含中文或数字的能力。
    - 首个中文字符串捕获为角色名，若不包含则返回 ``all`` 请求角色面板列表数据
    - 首个数字字符串捕获为 UID，若不包含则返回 ``uidHelper()`` 根据绑定配置查找的 UID

    * ``param msg: str`` 输入消息，由 ``state["_prefix"]["command_arg"]`` 或 ``event.get_plaintext()`` 生成，可能包含 CQ 码
    * ``param qq: str`` 输入消息触发 QQ
    * ``param atqq: str = ""`` 输入消息中首个 at 的 QQ
    - ``return: Tuple[str, str]``  UID、角色名
    """
    uid, char = "", ""
    group = findall(r"[0-9]+|[\u4e00-\u9fa5]+", sub(r"\[CQ:.*\]", "", msg))
    for s in group:
        if str(s).isdigit() and not uid:
            uid = str(s)
        elif not str(s).isdigit() and not char:
            char = str(s)
    uid = uid or await uidHelper(atqq or qq)
    char = char or "all"
    return uid, char


@driver.on_startup
async def exStartup() -> None:
    await fetchInitRes()


@showPanel.handle()
async def giveMePower(bot: Bot, event: MessageEvent, state: T_State):
    qq = str(event.get_user_id())
    argsMsg = (  # 获取不包含触发关键词的消息文本
        str(state["_prefix"]["command_arg"])
        if "command_arg" in list(state.get("_prefix", {}))
        else str(event.get_plaintext())
    )
    # await showPanel.finish(argsMsg)
    # 提取消息中的 at 作为操作目标 QQ
    opqq = ""
    for seg in event.message:
        if seg.type == "at" and not opqq:
            opqq = str(seg.data["qq"])
            break
    # 输入以「绑定」开头，识别为绑定操作
    if argsMsg.startswith("绑定"):
        args = [a.strip() for a in argsMsg[2:].split(" ") if a.strip().isdigit()]
        if len(args) == 1:
            uid, opqq = args[0], opqq or qq
        elif len(args) == 2 and not opqq:
            uid, opqq = args[0], args[1]
        else:
            await showPanel.finish("面板绑定参数格式错误！")
        if opqq != qq and opqq not in bot.config.superusers:
            await showPanel.finish(f"没有权限操作 QQ{qq} 的绑定状态！")
        elif uid[0] not in ["1", "2", "5", "7", "8"] or len(uid) > 9:
            await showPanel.finish(f"UID 是「{uid}」吗？好像不对劲呢..")
        await showPanel.finish(await uidHelper(opqq, uid))
    # 尝试从输入中理解 UID、角色名
    uid, char = await formatInput(argsMsg, qq, opqq)
    logger.info(f"可能需要查找 UID{uid} 的「{char}」角色面板..")
    if not uid.isdigit() or uid[0] not in ["1", "2", "5", "7", "8"] or len(uid) > 9:
        await showPanel.finish(f"UID 是「{uid}」吗？好像不对劲呢..")
    rt = await getPanelMsg(uid, char)
    if rt.get("error") or rt.get("msg"):
        await showPanel.finish(rt.get("error") or rt.get("msg"))
    if rt.get("pic"):
        await showPanel.finish(MessageSegment.image(rt["pic"]))
