from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiohttp_jinja2 import APP_KEY as JINJA2_APP_KEY
import sqlite3
from .router import setup_routes
from .middlewares import connect_db, session_middleware, cors_middleware
import aiohttp_session


THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


def create_db(app):
    conn = sqlite3.connect("stubs.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists stubs
                 (id integer primary key,
                  stubbed_url text unique,
                  content text,
                  timestamp text,
                  ip text)""")

    conn.commit()
    conn.close()


@jinja2.contextfilter
def reverse_url(context, name, **parts):
    """
    jinja2 filter for generating urls,
    see http://aiohttp.readthedocs.io/en/stable/web.html#reverse-url-constructing-using-named-resources
    Usage:
    {%- raw %}
      {{ 'the-view-name'|url }} might become "/path/to/view"
    or with parts and a query
      {{ 'item-details'|url(id=123, query={'active': 'true'}) }} might become "/items/1?active=true
    {%- endraw %}
    see app/templates.index.jinja for usage.
    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param name: the name of the route
    :param parts: url parts to be passed to route.url(), if parts includes "query" it's removed and passed seperately
    :return: url as generated by app.route[<name>].url(parts=parts, query=query)
    """
    app = context['app']

    kwargs = {}
    if 'query' in parts:
        kwargs['query'] = parts.pop('query')
    if parts:
        kwargs['parts'] = parts
    return app.router[name].url(**kwargs)


@jinja2.contextfilter
def static_url(context, static_file_path):
    """
    jinja2 filter for generating urls for static files. NOTE: heed the warning in create_app about "static_root_url"
    as this filter uses app['static_root_url'].
    Usage:
    {%- raw %}
      {{ 'styles.css'|static }} might become "http://mycdn.example.com/styles.css"
    {%- endraw %}
    see app/templates.index.jinja for usage.
    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param static_file_path: path to static file under static route
    :return: roughly just "<static_root_url>/<static_file_path>"
    """
    app = context['app']
    try:
        static_url = app['static_root_url']
    except KeyError:
        raise RuntimeError('app does not define a static root url "static_root_url"')
    return '{}/{}'.format(static_url.rstrip('/'), static_file_path.lstrip('/'))


@jinja2.contextfunction
def get_flash_messages(context):
    _flash_messages = context['request']['session'].get('_flash_messages', [])

    while len(_flash_messages) > 0:
        yield _flash_messages.pop()

    context['request']['session']['_flash_messages'] = []


aiohttp_session_middleware = aiohttp_session.session_middleware(
    aiohttp_session.SimpleCookieStorage()
)


app = web.Application(
    middlewares=[
        connect_db,
        aiohttp_session_middleware,
        session_middleware,
        cors_middleware
    ]
)

app.on_startup.append(create_db)

app['static_root_url'] = '/static/'

setup_routes(app)

jinja2_loader = jinja2.FileSystemLoader(str(THIS_DIR / 'templates'))

aiohttp_jinja2.setup(app,
    loader=jinja2_loader,
    context_processors=[aiohttp_jinja2.request_processor],
    app_key=JINJA2_APP_KEY)

app[JINJA2_APP_KEY].filters.update(
    url=reverse_url,
    static=static_url,
)

app[JINJA2_APP_KEY].globals.update(
    get_flash_messages=get_flash_messages
)
