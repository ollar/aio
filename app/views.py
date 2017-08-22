from aiohttp import web
import aiohttp_jinja2
import datetime
import sqlite3
import json
import pdb
from aiohttp_session import get_session


@aiohttp_jinja2.template('home.html')
async def index(request):
    cursor = request.app['db_cursor']
    cursor.execute("select * from stubs")
    urls = cursor.fetchall()

    session = await get_session(request)

    # print(session)

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
            # flash("Incorrect data", "error")
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
            # flash("Such stub already exists", "error")
            return web.HTTPFound(self.home_url)

        # flash("Url added successfully")
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
            # flash("No such stub, sorry", "error")
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
            # flash("Incorrect data", "error")
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
            # flash("Stub updated succesfully")
        except sqlite3.IntegrityError:
            # flash("Such stub already exists", "error")
            return web.HTTPFound(self.edit_stub_url)

        except:
            # flash("OOps, an error occupied, sorry", "error")
            pass

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

    async def get(self):
        entry = self.get_entry(self.stubbed_url)

        if entry:
            try:
                return web.json_response(json.loads(entry[2]))
            except:
                return web.Response(text=entry[2])

        else:
            # flash("No such stub, sorry", "error")
            print("No such stub, sorry", "error")
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
                # flash("Stub removed succesfully")
                print("Stub removed succesfully")
            except:
                # flash("OOps, an error occupied, sorry", "error")
                print("OOps, an error occupied, sorry", "error")
                pass
            finally:
                return web.HTTPFound(self.home_url)

        return self.get()
