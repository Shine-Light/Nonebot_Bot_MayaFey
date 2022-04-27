"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 19:55
"""
from nonebot import logger, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from ..utils.admin_tools import banSb, image_moderation_async


find_pic = on_message(priority=12, block=False)
@find_pic.handle()
async def check_pic(bot: Bot, event: GroupMessageEvent):
    uid = [event.get_user_id()]
    gid = event.group_id
    eid = event.message_id
    if isinstance(event, MessageEvent):
        for msg in event.message:
            if msg.type == "image":
                url: str = msg.data["url"]
                image_ = url
                # result = await pic_ban_cof(url=image_)
                result = (await image_moderation_async(image_))
                label = result["message"]
                if label == "Porn":
                    label = "色情"
                if label == "Sexy":
                    label = "性感"
                if label == "Illegal":
                    label = "违法"
                if label == "Ad":
                    label = "广告"
                if label == "Terror":
                    label = "暴恐"
                if label == "Polity":
                    label = "政治"
                if label == "Abuse":
                    label = "谩骂"
                # if label == "Illegal" or label == "Ad" or label == "Terror" or label == "Polity" or label == "Abuse":
                #     result["status"] = True

                if not result["status"]:
                    try:
                        await bot.delete_msg(message_id=eid)
                        logger.info('检测到违规图片，撤回')
                    except ActionFailed:
                        logger.info('检测到违规图片，但权限不足，撤回失败')
                    baning = banSb(gid, ban_list=uid, time=300)
                    async for baned in baning:
                        if baned:
                            try:
                                await baned
                            except ActionFailed:
                                await find_pic.finish("检测到违规图片，但权限不足")
                                logger.info('检测到违规图片，但权限不足，禁言失败')
                            else:
                                await bot.send(event=event, message=f"发送了违规图片,类型{label},现对你进行处罚,有异议请联系管理员", at_sender=True)
                                logger.info(f"检测到违规图片，禁言操作成功，用户: {uid[0]}")
                    logger.info('检测到违规内容')
                elif result["status"] == 'error':
                    logger.info(f"图片检测失败{result['message']}")
                elif result["status"]:
                    logger.info(f"图片安全")