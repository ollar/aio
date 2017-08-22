from aiohttp import web
import aiohttp_jinja2
import datetime
import sqlite3
import pdb

@aiohttp_jinja2.template('home.html')
def index(request):
    cursor = request.app['db_cursor']
    cursor.execute("select * from stubs")
    urls = cursor.fetchall()

    return {
        "urls": urls
    }


@aiohttp_jinja2.template('updateStub.html')
def add_stub_get(request):
    action_url = request.app.router['add_stub_get'].url_for()

    title = 'Create new stub'

    return {
            "stub": [],
            "action_url": action_url,
            "title": title
        }


async def add_stub_post(request):
    current_url = request.rel_url
    home_url = request.app.router['home'].url_for()
    db = request.app['sqlite_db']
    cursor = request.app['db_cursor']
    data = await request.post()

    if not data.get("url") or not data.get("content"):
        # flash("Incorrect data", "error")
        return web.HTTPFound(current_url)

    try:
        # # Insert a row of data
        cursor.execute("""INSERT INTO stubs (
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
        db.commit()

    except sqlite3.IntegrityError:
        # flash("Such stub already exists", "error")
        return web.HTTPFound(home_url)

    # flash("Url added successfully")
    return web.HTTPFound(home_url)


@aiohttp_jinja2.template('updateStub.html')
def edit_stub_get(request):
    cursor = request.app['db_cursor']
    stubbed_url = request.match_info['stubbed_url']

    cursor.execute("select * from stubs where stubbed_url=?", (stubbed_url,))
    entry = cursor.fetchone()

    edit_stub_url = request.app.router['edit_stub_post'].url_for(stubbed_url=stubbed_url)
    home_url = request.app.router['home'].url_for()

    if not entry:
        # flash("No such stub, sorry", "error")
        return web.HTTPFound(home_url)


    title = 'Update stub'

    return {
       "stub": entry,
       "action_url": edit_stub_url,
       "title": title
    }


async def edit_stub_post(request):
    data = await request.post()
    stubbed_url = request.match_info['stubbed_url']
    home_url = request.app.router['home'].url_for()
    edit_stub_url = request.app.router['edit_stub_get'].url_for(stubbed_url=stubbed_url)
    db = request.app['sqlite_db']
    cursor = request.app['db_cursor']

    print(data)

    if not data.get("url") or not data.get("content"):
        # flash("Incorrect data", "error")
        return web.HTTPFound(edit_stub_url)

    try:
        cursor.execute("""UPDATE stubs
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

        db.commit()
        # flash("Stub updated succesfully")
    except sqlite3.IntegrityError:
        # flash("Such stub already exists", "error")
        return web.HTTPFound(edit_stub_url)

    except:
        # flash("OOps, an error occupied, sorry", "error")
        pass

    return web.HTTPFound(home_url)
