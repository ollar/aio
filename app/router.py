from .views import index, add_stub_get, add_stub_post, edit_stub_get, edit_stub_post
import os


def setup_routes(app):
    app.router.add_get('/', index, name='home')

    app.router.add_get('/add', add_stub_get, name='add_stub_get')
    app.router.add_post('/add', add_stub_post, name='add_stub_post')

    app.router.add_get('/stub/{stubbed_url}/edit', edit_stub_get, name='edit_stub_get')
    app.router.add_post('/stub/{stubbed_url}/edit', edit_stub_post, name='edit_stub_post')

    app.router.add_get('/stub/{stubbed_url}', index, name='stub')
    app.router.add_post('/stub/{stubbed_url}', index, name='stub_post')

    app.router.add_static('/static/',
                          path=str(
                            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
                          ),
                          name='static')
