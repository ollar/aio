from aiohttp import web
import aiohttp_jinja2
import datetime
import sqlite3
import json
from .utils import flash
from .crawler import Crawler


@aiohttp_jinja2.template('home.html')
async def index(request):
    cursor = request.app['db_cursor']
    cursor.execute("select * from stubs")
    urls = cursor.fetchall()

    return {
        "urls": urls
    }


class AddStub(web.View):
    def __init__(self, request, *args):
        super().__init__(request)

        self.action_url = request.app.router['add_stub'].url_for()
        self.current_url = request.rel_url
        self.home_url = request.app.router['home'].url_for()

        self.db = request.app['sqlite_db']
        self.cursor = request.app['db_cursor']

    @aiohttp_jinja2.template('updateStub.html')
    async def get(self):
        title = 'Create new stub'

        return {
            "stub": [],
            "action_url": self.action_url,
            "title": title
        }

    async def post(self):
        data = await self._request.post()

        if not data.get("url") or not data.get("content"):
            flash(self._request, "Incorrect data", "error")
            return web.HTTPFound(self.current_url)

        try:
            # # Insert a row of data
            self.cursor.execute("""INSERT INTO stubs (
                    stubbed_url,
                    content,
                    timestamp,
                    ip
                ) VALUES (?,?,?,?)""", (
                    data.get("url"),
                    data.get("content"),
                    str(datetime.datetime.now()),
                    # request.remote_addr)
                    'ip here')
                )
            self.db.commit()

        except sqlite3.IntegrityError:
            flash(self._request, "Such stub already exists", "error")
            return web.HTTPFound(self.home_url)

        flash(self._request, "Url added successfully")
        return web.HTTPFound(self.home_url)


class UpdateStub(web.View):
    def __init__(self, request):
        super().__init__(request)

        self.cursor = request.app['db_cursor']
        self.db = request.app['sqlite_db']

        self.stubbed_url = request.match_info['stubbed_url']

        self.edit_stub_url = request.app.router['edit_stub']\
            .url_for(stubbed_url=self.stubbed_url)

        self.home_url = request.app.router['home'].url_for()

    @aiohttp_jinja2.template('updateStub.html')
    def get(self):
        self.cursor.execute("""SELECT *
                                FROM stubs
                                WHERE stubbed_url=?""",
                            (self.stubbed_url,)
                            )
        entry = self.cursor.fetchone()

        if not entry:
            flash(self._request, "No such stub, sorry", "error")
            return web.HTTPFound(self.home_url)

        title = 'Update stub'

        return {
           "stub": entry,
           "action_url": self.edit_stub_url,
           "title": title
        }

    async def post(self):
        data = await self._request.post()

        if not data.get("url") or not data.get("content"):
            flash(self._request, "Incorrect data", "error")
            return web.HTTPFound(self.edit_stub_url)

        try:
            self.cursor.execute("""UPDATE stubs
                                   SET stubbed_url = ?,
                                       content = ?,
                                       timestamp = ?,
                                       ip = ?
                                   WHERE id =? """, (
                                        data.get('url'),
                                        data.get('content'),
                                        str(datetime.datetime.now()),
                                        'ip here',
                                        data.get('id'),))

            self.db.commit()
            flash(self._request, "Stub updated succesfully")
        except sqlite3.IntegrityError:
            flash(self._request, "Such stub already exists", "error")
            return web.HTTPFound(self.edit_stub_url)

        except:
            flash(self._request, "OOps, an error occupied, sorry", "error")

        return web.HTTPFound(self.home_url)


class Stub(web.View):
    def __init__(self, request):
        super().__init__(request)

        self.cursor = request.app['db_cursor']
        self.db = request.app['sqlite_db']

        self.home_url = request.app.router['home'].url_for()
        self.stubbed_url = request.match_info['stubbed_url']

    def get_entry(self, stubbed_url):
        self.cursor.execute("""SELECT *
                            FROM stubs
                            WHERE stubbed_url=?""",
                            (stubbed_url,))
        return self.cursor.fetchone()

    async def options(self, *args, **kwargs):
        return web.Response(headers={
            'Access-Control-Allow-Headers': self._request.headers.get('Access-Control-Request-Headers', '')
        })

    async def get(self, is_redirect=False):
        entry = self.get_entry(self.stubbed_url)

        if entry:
            try:
                return web.json_response(json.loads(entry[2]))
            except:
                return web.Response(text=entry[2])

        else:
            flash(self._request, "No such stub, sorry", "error")

        if is_redirect:
            return web.json_response({'error': 'not_found'})

        return web.HTTPFound(self.home_url)

    async def post(self):
        data = await self._request.post()

        if data.get('_method') == 'DELETE':
            try:
                self.cursor.execute("""DELETE
                                       FROM stubs
                                       WHERE id=?""",
                                    (data.get('id'),))
                self.db.commit()
                flash(self._request, "Stub removed succesfully")

            except:
                flash(self._request, "OOps, an error occupied, sorry", "error")

            finally:
                return web.HTTPFound(self.home_url)

        return await self.get(True)

    async def put(self):
        return await self.get(True)

    async def patch(self):
        return await self.get(True)

    async def delete(self):
        return await self.get(True)


class CrawlerManager(web.View):
    def __init__(self, request):
        super().__init__(request)

        self.action_url = request.app.router['crawler']\
            .url_for()
        self.home_url = request.app.router['home'].url_for()

        self.db = request.app['sqlite_db']
        self.cursor = request.app['db_cursor']

    @aiohttp_jinja2.template('crawler.html')
    def get(self):
        return {
            'action_url': self.action_url,
        }

    async def post(self):
        data = await self._request.post()

        if not data.get("base-url") or not data.get("username") or not data.get("password"):
            flash(self._request, "Incorrect data", "error")
            return web.HTTPFound(self.action_url)

        crawler = Crawler(db=self.db, cursor=self.cursor, loop=self._request.app.loop, **data)
        await crawler()

        return web.HTTPFound(self.home_url)


