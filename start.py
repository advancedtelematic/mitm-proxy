import logging
import sys

from argparse import ArgumentParser
from os import path
from typing import Any, Dict

from api.config import Config
from api.flow import Flow
from api.http import HttpServer
from api.proxy import Proxy


LOG_FORMAT = "%(levelname)s (%(filename)s:%(lineno)s) @ %(asctime)s: %(message)s"

def main() -> None:
    """Start the API for controlling mitmproxy."""
    if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 required")

    log = start_logger()
    args = parse_args()
    log.debug(f"starting with arguments: {args}")

    config = Config(args)
    flow = Flow(config)
    proxy = Proxy(flow)
    http = HttpServer(proxy)
    http.start()

def start_logger() -> logging.Logger:
    """Set up project-wide logging."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    return logger

def parse_args() -> Dict[str, Any]:
    """Parse the command-line arguments."""
    parser = ArgumentParser(path.basename(__file__), description="TUF metadata MITM proxy")

    parser.add_argument("--http.host", type=str, default="127.0.0.1", help="Set the API host.")
    parser.add_argument("--http.port", type=int, default=5555, help="Set the API port.")

    parser.add_argument("--flow.root", type=str, required=True, help="Directory containing the available mitmproxy flows.")
    parser.add_argument("--flow.initial", type=str, help="The initial flow filename to run on startup.")

    parser.add_argument("--mitm.cadir", type=str, required=True, help="Set the --cadir mitmproxy flag.")
    parser.add_argument("--mitm.client_certs", type=str, required=True, help="Set the --client-certs mitmproxy flag.")
    parser.add_argument("--mitm.upstream_trusted_ca", type=str, required=True, help="Set the --upstream-trusted-ca mitmproxy flag.")

    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
