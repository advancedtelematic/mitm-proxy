import asyncio
import logging
import sys

from argparse import ArgumentParser, Namespace
from os import path
from signal import SIGINT, SIGTERM, signal
from types import FrameType

from .api import HttpServer
from .config import Config
from .proxy import Proxy
from .utils import JsonFormatter


def main() -> None:
    """Start MITM proxy with an HTTP server for control."""
    if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 required")

    log = start_logger()
    args = parse_args()
    log.debug(f"Starting MITM proxy with args: {args}")

    for sig in [SIGINT, SIGTERM]:
        signal(sig, quit)

    config = Config(args)
    proxy = Proxy(config)

    server = HttpServer(config, proxy)
    loop = new_event_loop()
    server.start(loop)


def start_logger() -> logging.Logger:
    """Set up proxy logging."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    return logger

def parse_args() -> Namespace:
    """Parse the command-line arguments."""
    parser = ArgumentParser(path.basename(__file__), description="TUF metadata MITM proxy")

    parser.add_argument("debug", type=bool, default=True, help="Enable debugging.")
    parser.add_argument("host", type=str, default="127.0.0.1", help="Set the API host.")
    parser.add_argument("port", type=int, default=5456, help="Set the API port.")

    return parser.parse_args()

def new_event_loop() -> asyncio.AbstractEventLoop:
    """Start a new event loop."""
    return asyncio.get_event_loop()

def quit(signum: int, frame: FrameType) -> None:
    """Shutdown all handlers."""
    sys.exit()


if __name__ == '__main__':
    main()
