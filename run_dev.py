from app.main import app
from aiohttp.web import run_app


run_app(app, host="0.0.0.0", port=5001)
