from app.main import app
from aiohttp import web


web.run_app(app, host="0.0.0.0", port=5001)
