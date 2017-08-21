from aiohttp import web
import aiohttp_jinja2
import datetime
import sqlite3


def index(request):
    return web.Response(text='index')


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
    data = await request.post()

    if not data.get("url") or not data.get("content"):
        # flash("Incorrect data", "error")
        return 'ok'
        # return redirect(url_for("home"))

    try:
        # # Insert a row of data
        g.db_cursor.execute("""INSERT INTO stubs (
                stubbed_url,
                content,
                timestamp,
                ip
            ) VALUES (?,?,?,?)""", (
                request.form.get("url"),
                request.form.get("content"),
                str(datetime.datetime.now()),
                request.remote_addr)
            )
        g.sqlite_db.commit()

    except sqlite3.IntegrityError:
        flash("Such stub already exists", "error")
        return redirect(url_for("home"))

    # flash("Url added successfully")
    return 'ok'