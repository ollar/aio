from .views import index, AddStub, UpdateStub, Stub
import os


def setup_routes(app):
    app.router.add_get('/', index, name='home')

    app.router.add_route('*', '/add', AddStub, name='add_stub')
    app.router.add_route('*', '/stub/{stubbed_url:.*}/edit', UpdateStub, name='edit_stub')
    app.router.add_route('*', '/stub/{stubbed_url:.*}', Stub, name='stub')

    app.router.add_static('/static/',
                          path=str(
                            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
                          ),
                          name='static')
