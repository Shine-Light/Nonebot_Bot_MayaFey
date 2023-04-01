"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/8/15 16:11
"""
from nonebot import on_command, require, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg

from utils.matcherManager import matcherManager
from utils.other import add_target, get_bot_name
from .GenshinPray import GenshinPray, database
from .tools import CommandUrl


genshinpray = GenshinPray()

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="GenshinPray",
    description="模拟原神祈愿,默认每抽消耗 1 积分,可修改",
    usage="/角色祈愿 单|十抽 {蛋池编号}\n"
          "/常驻祈愿 单|十抽\n"
          "/全角色祈愿 单|十抽\n"
          "/武器祈愿 单|十抽\n"
          "/全武器祈愿 单|十抽\n"
          "/武器定轨 {武器名}\n"
          "/查询定轨\n"
          "/祈愿蛋池列表\n"
          "/祈愿蛋池详情 {蛋池编号}|武器\n"
          "/我的祈愿\n"
          "/我的祈愿记录 (显示前20条4,5星记录)\n"
          "/祈愿排行榜\n"
          "/祈愿费用\n"
          "/设置祈愿费用 {积分数} (超级用户)\n"
          "/自定义祈愿角色池 {蛋池编号} {1个5星和3个4星,用空格隔开} (超级用户)\n"
          "/自定义原神武器池 {2个5星和5个4星,用空格隔开} (超级用户)\n"
          "/清空原神角色池 (超级用户)\n"
          "/清空原神武器池 (超级用户)\n"
          "/设置祈愿服装概率 {概率} (0~100)\n"
          "不知道角色或武器全称?前往官方wiki查看:https://bbs.mihoyo.com/ys/obc/?bbs_presentation_style=no_header" + add_target(60),
    extra={
        "generate_type": "group",
        "permission_common": "member",
        "permission_special": {
            "GenshinPray:SetPolePond": "superuser",
            "GenshinPray:SetArmPond": "superuser",
            "GenshinPray:ResetArmPond": "superuser",
            "GenshinPray:ResetRolePond": "superuser",
            "GenshinPray:SetSkinRate": "superuser",
            "GenshinPray:SetOneCost": "superuser",
        },
        "unset": False,
        "total_unable": False,
        "author": "Shine_Light",
        "translate": "原神祈愿",
    }
)

RolePray = on_command(cmd="角色祈愿", aliases={"UP祈愿", "UP角色祈愿", "角色UP祈愿"}, priority=8)
@RolePray.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await RolePray.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    error = await genshinpray.init_with_gid(gid)
    if error:
        await RolePray.finish(f"初始化出错:{error}")
    args = args.extract_plain_text().strip()
    args = args.split(" ")
    if len(args) != 2:
        await RolePray.finish("参数有误!在检查一下")

    count = args[0]

    try:
        pondID = int(args[1])
    except:
        await RolePray.finish(f"没有 {args[1]} 这个蛋池编号哟")

    # 十连
    if count in ["10抽", "十抽", "拾抽", "10连", "十连", "拾连", "10连抽", "十连抽", "拾连抽"]:
        result = await GenshinPray.Pray(CommandUrl.RolePray_Ten, gid, uid, pondID, 10, nickname)
    # 单抽
    elif count in ["1抽", "单抽", "壹抽"]:
        result = await GenshinPray.Pray(CommandUrl.RolePray_One, gid, uid, pondID, 1, nickname)
    else:
        await RolePray.finish(f"没有 {count} 这种抽法诶")

    if not result.code.is_success():
        await RolePray.finish(result.code.to_String())

    await RolePray.send(Message([MessageSegment.image(result.imgUrl)]), at_sender=True)

PermPray = on_command(cmd="常驻祈愿", priority=8)
@PermPray.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await PermPray.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    error = await genshinpray.init_with_gid(gid)
    if error:
        await PermPray.finish(f"初始化出错:{error}")
    count = args.extract_plain_text().strip()

    if not count:
        await PermPray.finish("你还没说要抽几次呢")

    # 十连
    if count in ["10抽", "十抽", "拾抽", "10连", "十连", "拾连", "10连抽", "十连抽", "拾连抽"]:
        result = await GenshinPray.Pray(CommandUrl.PermPray_Ten, gid, uid, 0, 10, nickname)
    # 单抽
    elif count in ["1抽", "单抽", "壹抽"]:
        result = await GenshinPray.Pray(CommandUrl.PermPray_One, gid, uid, 0, 1, nickname)
    else:
        await PermPray.finish(f"没有 {count} 这种抽法诶")

    if not result.code.is_success():
        await PermPray.finish(f"出错啦,{result.code.to_String()}")

    await PermPray.send(Message([MessageSegment.image(result.imgUrl)]), at_sender=True)

ArmPray = on_command(cmd="武器祈愿", priority=8)
@ArmPray.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await ArmPray.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    error = await genshinpray.init_with_gid(gid)
    if error:
        await ArmPray.finish(f"初始化出错:{error}")
    count = args.extract_plain_text().strip()

    if not count:
        await ArmPray.finish("你还没说要抽几次呢")

    # 十连
    if count in ["10抽", "十抽", "拾抽", "10连", "十连", "拾连", "10连抽", "十连抽", "拾连抽"]:
        result = await GenshinPray.Pray(CommandUrl.ArmPray_Ten, gid, uid, 0, 10, nickname)
    # 单抽
    elif count in ["1抽", "单抽", "壹抽"]:
        result = await GenshinPray.Pray(CommandUrl.ArmPray_One, gid, uid, 0, 1, nickname)
    else:
        await ArmPray.finish(f"没有 {count} 这种抽法诶")

    if not result.code.is_success():
        await ArmPray.finish(f"出错啦,{result.code.to_String()}")

    await ArmPray.send(Message([MessageSegment.image(result.imgUrl)]), at_sender=True)

FullRolePray = on_command(cmd="全角色祈愿", priority=8)
@FullRolePray.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await FullRolePray.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    error = await genshinpray.init_with_gid(gid)
    if error:
        await FullRolePray.finish(f"初始化出错:{error}")
    count = args.extract_plain_text().strip()

    if not count:
        await FullRolePray.finish("你还没说要抽几次呢")

    # 十连
    if count in ["10抽", "十抽", "拾抽", "10连", "十连", "拾连", "10连抽", "十连抽", "拾连抽"]:
        result = await GenshinPray.Pray(CommandUrl.FullRolePray_Ten, gid, uid, 0, 10, nickname)
    # 单抽
    elif count in ["1抽", "单抽", "壹抽"]:
        result = await GenshinPray.Pray(CommandUrl.FullRolePray_One, gid, uid, 0, 1, nickname)
    else:
        await FullRolePray.finish(f"没有 {count} 这种抽法诶")

    if not result.code.is_success():
        await FullRolePray.finish(f"出错啦,{result.code.to_String()}")

    await FullRolePray.send(Message([MessageSegment.image(result.imgUrl)]), at_sender=True)

FullArmPray = on_command(cmd="全武器祈愿", priority=8)
@FullArmPray.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await FullArmPray.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    error = await genshinpray.init_with_gid(gid)
    if error:
        await FullArmPray.finish(f"初始化出错:{error}")
    count = args.extract_plain_text().strip()

    if not count:
        await FullArmPray.finish("你还没说要抽几次呢")

    # 十连
    if count in ["10抽", "十抽", "拾抽", "10连", "十连", "拾连", "10连抽", "十连抽", "拾连抽"]:
        result = await GenshinPray.Pray(CommandUrl.FullArmPray_Ten, gid, uid, 0, 10, nickname)
    # 单抽
    elif count in ["1抽", "单抽", "壹抽"]:
        result = await GenshinPray.Pray(CommandUrl.FullArmPray_One, gid, uid, 0, 1, nickname)
    else:
        await FullArmPray.finish(f"没有 {count} 这种抽法诶")

    if not result.code.is_success():
        await FullArmPray.finish(f"出错啦,{result.code.to_String()}")

    await FullArmPray.send(Message([MessageSegment.image(result.imgUrl)]))

SetAssign = on_command(cmd="武器定轨", aliases={"定轨武器"}, priority=8)
@SetAssign.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await SetAssign.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    uid = str(event.user_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetAssign.finish(f"初始化出错:{error}")
    nickname = (await bot.get_group_member_info(group_id=int(gid), user_id=int(uid), no_cache=True))["nickname"]
    goodsName = args.extract_plain_text().strip()

    if not goodsName:
        await SetAssign.finish("要定轨的武器呢?")

    result = GenshinPray.Assign(gid, uid, goodsName, nickname)

    if not result.code.is_success():
        await SetAssign.finish(result.code.to_String())

    await SetAssign.send("设置成功!")

GetAssign = on_command(cmd="查询定轨", aliases={"定轨查询"}, priority=8)
@GetAssign.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetAssign.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetAssign.finish(f"初始化出错:{error}")
    uid = str(event.user_id)
    result = GenshinPray.get_Assign(gid, uid)

    if not result.code.is_success():
        await GetAssign.finish(result.code.to_String())

    await GetAssign.send(result.message, at_sender=True)

GetPondInfoList = on_command(cmd="祈愿蛋池列表", priority=8)
@GetPondInfoList.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetPondInfoList.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetPondInfoList.finish(f"初始化出错:{error}")
    result = GenshinPray.GetPondList(gid)

    if not result.code.is_success():
        await GetPondInfoList.finish(result.code.to_String())

    await GetPondInfoList.send(result.message, at_sender=True)

GetPondInfo = on_command(cmd="祈愿蛋池详情", aliases={"祈愿蛋池信息"}, priority=8)
@GetPondInfo.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await GetPondInfo.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetPondInfo.finish(f"初始化出错:{error}")
    args = args.extract_plain_text().strip()

    if not args:
        await GetPondInfo.finish("你想看哪个池子的信息呢?")

    try:
        pondId = int(args)
    except:
        if args not in ["武器", "武器池"]:
            await GetPondInfo.finish(f"没有 {args} 这个池子")

    if args in ["武器", "武器池"]:
        result = await GenshinPray.GetArmPondInfo(gid)
    else:
        result = await GenshinPray.GetRolePondInfo(gid, pondId)

    if not result.code.is_success():
        await GetPondInfo.finish(result.code.to_String())

    await GetPondInfo.send(MessageSegment.image(result.imgUrl), at_sender=True)

GetMyPrayDetail = on_command(cmd="我的祈愿", aliases={"查询我的祈愿"}, priority=8)
@GetMyPrayDetail.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetMyPrayDetail.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetMyPrayDetail.finish(f"初始化出错:{error}")
    uid = str(event.user_id)

    result = await GenshinPray.GetMemberPrayDetail(gid, uid)

    if not result.code.is_success():
        await GetMyPrayDetail.finish(result.code.to_String())

    await GetMyPrayDetail.send(MessageSegment.image(result.imgUrl), at_sender=True)

GetMyPrayRecord = on_command(cmd="我的祈愿记录", aliases={"查询我的祈愿记录", "祈愿记录"}, priority=8)
@GetMyPrayRecord.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetMyPrayRecord.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetMyPrayRecord.finish(f"初始化出错:{error}")
    uid = str(event.user_id)
    bot_id = event.self_id

    result = GenshinPray.GetMemberPrayRecord(gid, uid)

    if not result.code.is_success():
        await GetMyPrayRecord.finish(result.code.to_String())

    message = []
    for msg in result.message:
        message.append(
            MessageSegment.node_custom(
                bot_id,
                get_bot_name(),
                msg
            )
        )

    await bot.call_api(api="send_group_forward_msg", group_id=int(gid), messages=message)

GetLuckRanking = on_command(cmd="祈愿排行榜", aliases={"原神欧皇排行榜", "祈愿欧皇排行榜"}, priority=8)
@GetLuckRanking.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetLuckRanking.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await GetLuckRanking.finish(f"初始化出错:{error}")

    result = GenshinPray.GetLuckRanking(gid)

    if not result.code.is_success():
        await GetLuckRanking.finish(result.code.to_String())

    await GetLuckRanking.send(result.message)

SetRolePond = on_command(cmd="自定义祈愿角色池", aliases={"自定义原神角色池"}, priority=8)
matcherManager.addMatcher("GenshinPray:SetPolePond", SetRolePond)
@SetRolePond.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    if genshinpray.error:
        await SetRolePond.finish("该群聊未开启祈愿,或配置错误")
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetRolePond.finish(f"初始化出错:{error}")
    args = args.extract_plain_text().split(" ")
    if len(args) != 5:
        await SetRolePond.finish("参数不对哦,要三个四星和一个五星角色的全称")
    try:
        pondId = int(args[0])
    except:
        await SetRolePond.finish("蛋池编号要整数哦")

    result = GenshinPray.SetRolePond(gid, pondId, args[1:])

    if not result.code.is_success():
        await SetRolePond.finish(result.code.to_String())

    await SetRolePond.send("设置成功!")

SetArmPond = on_command(cmd="自定义祈愿武器池", aliases={"自定义原神武器池"}, priority=8)
matcherManager.addMatcher("GenshinPray:SetArmPond", SetArmPond)
@SetArmPond.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    if genshinpray.error:
        await SetArmPond.finish("该群聊未开启祈愿,或配置错误")
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetArmPond.finish(f"初始化出错:{error}")
    args = args.extract_plain_text().split(" ")
    if len(args) != 7:
        await SetArmPond.finish("参数不对哦,要五个四星和两个五星武器的全称")

    result = GenshinPray.SetArmPond(gid, args)

    if not result.code.is_success():
        await SetArmPond.finish(result.code.to_String())

    await SetArmPond.send("设置成功!")

ResetArmPond = on_command(cmd="清空祈愿武器池", aliases={"重置祈愿武器池", "清空原神武器池", "重置原神武器池"}, priority=8)
matcherManager.addMatcher("GenshinPray:ResetArmPond", ResetArmPond)
@ResetArmPond.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    if genshinpray.error:
        await ResetArmPond.finish("该群聊未开启祈愿,或配置错误")
    error = await genshinpray.init_with_gid(gid)
    if error:
        await ResetArmPond.finish(f"初始化出错:{error}")
    result = GenshinPray.ResetArmPond(gid)

    if not result.code.is_success():
        await ResetArmPond.finish(result.code.to_String())

    await ResetArmPond.send("设置成功!")

ResetRolePond = on_command(cmd="清空祈愿角色池", aliases={"重置祈愿角色池", "清空原神角色池", "重置原神角色池"}, priority=8)
matcherManager.addMatcher("GenshinPray:ResetRolePond", ResetRolePond)
@ResetRolePond.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    if genshinpray.error:
        await ResetRolePond.finish("该群聊未开启祈愿,或配置错误")
    error = await genshinpray.init_with_gid(gid)
    if error:
        await ResetRolePond.finish(f"初始化出错:{error}")
    result = GenshinPray.ResetArmPond(gid)

    if not result.code.is_success():
        await ResetRolePond.finish(result.code.to_String())

    await ResetRolePond.send("设置成功!")

SetSkinRate = on_command(cmd="设置祈愿皮肤概率", aliases={"设置祈愿服装概率", "设定祈愿服装概率", "设定祈愿皮肤概率"}, priority=8)
matcherManager.addMatcher("GenshinPray:SetSkinRate", SetSkinRate)
@SetSkinRate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    if genshinpray.error:
        await SetSkinRate.finish("该群聊未开启祈愿,或配置错误")
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetSkinRate.finish(f"初始化出错:{error}")
    if not args.extract_plain_text().strip():
        await SetSkinRate.finish("概率呢?")
    try:
        rare = int(args.extract_plain_text())
    except:
        await SetSkinRate.finish("概率必须为整数")

    if not 0 <= rare <= 100:
        await SetSkinRate.finish("超出范围,范围为 0~100")

    result = GenshinPray.SetSkinRate(gid, rare=rare)

    if not result.code.is_success():
        await SetSkinRate.finish(result.code.to_String())

    await SetSkinRate.send("设置成功!")

SetOneCost = on_command(cmd="设置原神祈愿费用", aliases={"设定原神祈愿费用", "设定祈愿费用", "设置祈愿费用"}, priority=8)
matcherManager.addMatcher("GenshinPray:SetOneCost", SetOneCost)
@SetOneCost.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if genshinpray.error:
        await SetSkinRate.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetOneCost.finish(f"初始化出错:{error}")
    if not args.extract_plain_text().strip():
        await SetOneCost.finish("费用呢?")

    try:
        cost = int(args.extract_plain_text())
    except:
        await SetOneCost.finish("费用必须是整数!")

    if cost < 0:
        await SetOneCost.finish("不可以倒贴了啦!")

    result = GenshinPray.set_one_cost(gid, cost)

    if result:
        if cost >= 100:
            await SetOneCost.finish("设置成功!不过这价格有点高吧(小声比比)")
        elif cost == 0:
            await SetOneCost.finish("设置成功!老板真是财大气粗")
        await SetOneCost.send("设置成功!")

GetOneCost = on_command(cmd="原神祈愿费用", aliases={"祈愿费用"}, priority=8)
@GetOneCost.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if genshinpray.error:
        await GetOneCost.finish("该群聊未开启祈愿,或配置错误")
    gid = str(event.group_id)
    error = await genshinpray.init_with_gid(gid)
    if error:
        await SetOneCost.finish(f"初始化出错:{error}")

    cost = GenshinPray.get_one_cost(gid)

    await GetOneCost.send(f"当前群聊每次祈愿需花费 {cost} 积分")

scheduler = require("nonebot_plugin_apscheduler").scheduler
timezone = "Asia/Shanghai"
@scheduler.scheduled_job("interval", hours=4, timezone=timezone)
async def _():
    try:
        genshinpray.cursor.execute(f"USE {database};")
        genshinpray.cursor.execute("SELECT Id FROM authorize;")
        logger.info("执行防原神数据库断连")
    except Exception as e:
        logger.warning(f"执行防原神数据库断连失败,{str(e)}")
