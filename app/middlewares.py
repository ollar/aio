import sqlite3
from functools import partial
from .utils import flash
from aiohttp_session import get_session


async def connect_db(app, handler):
    async def middleware_handler(request):
        request.app['sqlite_db'] = sqlite3.connect("stubs.db")
        request.app['db_cursor'] = request.app['sqlite_db'].cursor()

        response = await handler(request)

        if hasattr(request.app, "sqlite_db"):
            request.app['sqlite_db'].close()

        return response

    return middleware_handler


async def session_middleware(app, handler):
    async def middleware_handler(request):
        session = await get_session(request)
        request['session'] = session

        return await handler(request)

    return middleware_handler


async def cors_middleware(app, handler):
    async def middleware_handler(request):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': 'authToken,If-None-Match,pageId,Content-Type'
        }

        response = await handler(request)

        response.headers.update(headers)

        return response

    return middleware_handler
