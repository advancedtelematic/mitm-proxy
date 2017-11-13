import logging as log
import sys

from argparse import ArgumentParser
from os import path
from typing import Any, Dict

from api.config import Config
from api.flow import Flow
from api.http import Server
from api.proxy import Proxy


LOG_FORMAT = "%(asctime)s - %(levelname)s (%(filename)s:%(lineno)s): %(message)s"
log.basicConfig(level=log.DEBUG, format=LOG_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")

def main() -> None:
    """Start the API for controlling mitmproxy."""
    if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 required")

    config = Config(parse_args())
    flow = Flow(config)
    proxy = Proxy(flow)
    http = Server(proxy)
    http.start()

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
