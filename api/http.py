import asyncio
import logging

from sanic import Sanic
from sanic.response import HTTPResponse
from sanic.request import Request, json

from .config import Config
from .flow import Flow
from .proxy import Proxy


log = logging.getLogger(__name__)

class HttpServer(object):
    """HTTP server used for setting the mitmproxy flow."""
    app: Sanic
    proxy: Proxy
    flow: Flow
    config: Config

    def __init__(self, proxy: Proxy) -> None:
        app = Sanic(__name__)
        app.add_route(self._handle_running, "/running")
        app.add_route(self._handle_config, "/config")

        self.app = app
        self.proxy = proxy
        self.flow = proxy.flow
        self.config = proxy.config

    def start(self) -> None:
        """Blocking call that starts the HTTP server."""
        (host, port) = self.config.http["host"], self.config.http["port"]
        log.info(f"starting an http server at http://{host}:{port}")

        server = self.app.create_server(host=host, port=port)
        asyncio.ensure_future(server)

        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        except Exception as e:
            log.error(f"http server failed: {e}")
            loop.stop()

    async def _handle_running(self, req: Request) -> HTTPResponse:
        return json({
            "running": f"{self.flow.get_running()}"
        })

    async def _handle_config(self, req: Request) -> HTTPResponse:
        return json(self.config)
