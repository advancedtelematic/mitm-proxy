from asyncio import AbstractEventLoop, ensure_future
from sanic import Sanic
from sanic.response import HTTPResponse
from sanic.request import Request, json

from .config import Config
from .proxy import Proxy


class HttpServer(object):
    """HTTP server used for setting the proxy handling procedures."""
    app: Sanic
    config: Config
    proxy: Proxy

    def __init__(self, config: Config, proxy: Proxy) -> None:
        app = Sanic(__name__)
        app.debug = config.app["debug"]

        app.add_route(self._handle_root, "/")
        app.add_route(self._handle_config, "/config")

        self.app = app
        self.config = config
        self.proxy = proxy

    def start(self, loop: AbstractEventLoop) -> None:
        """Start an async HTTP server on the given event loop."""
        server = self.app.create_server(
            host=self.config.api["host"],
            port=self.config.api["port"],
            debug=self.config.app["debug"]
        )

        ensure_future(server)
        try:
            loop.run_forever()
        except Exception:
            loop.stop()

    async def _handle_root(self, req: Request) -> HTTPResponse:
        return json({"path": "/"})

    async def _handle_config(self, req: Request) -> HTTPResponse:
        return json(self.config)
