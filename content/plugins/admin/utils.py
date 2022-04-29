"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/26 18:34
"""
import json
from typing import Optional
import aiofiles


# async def pic_cof(data: str, **kwargs) -> Optional[dict]:
#     try:
#         if kwargs['mode'] == 'url':
#             async with httpx.AsyncClient() as client:
#                 data_ = str(base64.b64encode((await client.get(url=data)).content), encoding='utf-8')
#             json_ = {"data": [f"data:image/png;base64,{data_}"]}
#         else:
#             json_ = {"data": [f"data:image/png;base64,{data}"]}
#     except Exception as err:
#         json_ = {"data": ["data:image/png;base64,"]}
#         print(err)
#     try:
#         async with httpx.AsyncClient() as client:
#             r = (await client.post(
#                 url='https://hf.space/gradioiframe/mayhug/rainchan-image-porn-detection/+/api/predict/',
#                 json=json_)).json()
#         if 'error' in r:
#             return None
#         else:
#             return r
#     except Exception as err:
#         logger.debug(f'于"utils.py"中的 pic_cof 发生错误：{err}')
#         return None
#
#
# async def pic_ban_cof(**data) -> Optional[bool]:
#     global result
#     if data:
#         if 'url' in data:
#             result = await pic_cof(data=data['url'], mode='url')
#         if 'base64' in data:
#             result = await pic_cof(data=data['data'], mode='default')
#         if result:
#             if result['data'][0]['label'] != 'safe':
#                 return True
#             else:
#                 return False
#         else:
#             return None


async def load(path) -> Optional[dict]:
    """
    加载json文件
    :return: Optional[dict]
    """
    try:
        async with aiofiles.open(path, mode='r', encoding="utf-8") as f:
            contents_ = await f.read()
            contents = json.loads(contents_)
            await f.close()
            return contents
    except FileNotFoundError:
        return None


async def upload(path, dict_content) -> None:
    """
    更新json文件
    :param path: 路径
    :param dict_content: python对象，字典
    """
    async with aiofiles.open(path, mode='w', encoding="utf-8") as c:
        await c.write(str(json.dumps(dict_content)))
        await c.close()
