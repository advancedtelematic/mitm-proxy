import logging as log

from sanic import Sanic
from sanic.config import Config as SanicConfig
from sanic.request import Request
from sanic.response import HTTPResponse, json

from .config import Config
from .flow import Flow
from .proxy import Proxy


class Server(object):
    """HTTP server used for setting the mitmproxy flow."""
    app: Sanic
    proxy: Proxy
    flow: Flow
    config: Config

    def __init__(self, proxy: Proxy) -> None:
        self.app = self._create_app()
        self.proxy = proxy
        self.flow = proxy.flow
        self.config = proxy.config

    def start(self) -> None:
        """Blocking call to start the HTTP server."""
        (host, port) = self.config.http["host"], self.config.http["port"]
        log.info(f"Starting an http server at http://{host}:{port}...")
        self.app.run(host=host, port=port)

    def _create_app(self) -> Sanic:
        """Create a new app with attached API routes."""
        SanicConfig.LOGO = ""
        app = Sanic(__name__, log_config=log.NOTSET)

        app.add_route(self._start, "/start/<name>", methods=['PUT'])
        app.add_route(self._stop, "/stop", methods=['PUT'])
        app.add_route(self._running, "/running")
        app.add_route(self._available, "/available")

        return app

    async def _start(self, req: Request, name: str) -> HTTPResponse:
        flow = self.flow.find(name)
        if not flow:
            return json({"error": "flow not found", "name": f"{name}"}, status=404)

        self.proxy.start(flow)
        return json({"started": f"{name}"})

    async def _stop(self, req: Request) -> HTTPResponse:
        running = self.flow.get_running()
        self.proxy.stop()
        return json({"stopped": f"{running}"})

    async def _running(self, req: Request) -> HTTPResponse:
        return json({"running": f"{self.flow.get_running()}"})

    async def _available(self, req: Request) -> HTTPResponse:
        return json({"available": [name for name in self.flow.available()]})
