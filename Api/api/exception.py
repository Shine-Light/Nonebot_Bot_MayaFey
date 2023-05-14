from fastapi import FastAPI
from fastapi.responses import JSONResponse
from nonebot import get_app
from nonebot.exception import ActionFailed
from .model import Result

app: FastAPI = get_app()


class AuthError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ParamError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@app.exception_handler(AuthError)
async def auth_error_handle(request, exception):
    return JSONResponse(
        status_code=401,
        content=Result(401, "身份验证无效或已过期!").dict()
    )


@app.exception_handler(ParamError)
async def param_error_handle(request, exception):
    return JSONResponse(
        status_code=200,
        content=Result(102, "参数错误").dict()
    )


@app.exception_handler(AttributeError)
async def attr_error_handle(request, exception):
    return JSONResponse(
        status_code=200,
        content=Result(102, "参数错误").dict()
    )


@app.exception_handler(ValueError)
async def bot_error_handle(request, exception: ValueError):
    if exception.args and exception.args[0] == 'There are no bots to get.':
        return JSONResponse(
            status_code=200,
            content=Result(102, "机器人未连接").dict()
        )
    else:
        raise exception


@app.exception_handler(ActionFailed)
async def action_error_handle(request, exception):
    return JSONResponse(
        status_code=200,
        content=Result(101, str(exception.info.get('message'))).dict()
    )

@app.exception_handler(FileNotFoundError)
async def file_error_handle(request, exception):
    return JSONResponse(
        status_code=200,
        content=Result(101, f"文件不存在,可能未初始化").dict()
    )
