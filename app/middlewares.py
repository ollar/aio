import sqlite3
from functools import partial
from .utils import flash

async def connect_db(app, handler):
    async def middleware_handler(request):
        request.app['sqlite_db'] = sqlite3.connect("stubs.db")
        request.app['db_cursor'] = request.app['sqlite_db'].cursor()

        response = await handler(request)

        if hasattr(request.app, "sqlite_db"):
            request.app['sqlite_db'].close()

        return response

    return middleware_handler


async def flashes_middleware(app, handler):
    async def middleware_handler(request):
        request['_flash'] = partial(flash, request)

        return await handler(request)

    return middleware_handler