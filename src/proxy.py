# -*- coding: utf-8 -*-
import random

from argparse import ArgumentParser
from consecution import Node, Pipeline
from enum import Enum
from mitmproxy import ctx
from mitmproxy.http import HTTPFlow as Flow
from os import path


class Mode(Enum):
    """Enumeration of all proxy modes."""
    Passive = Pipeline()


def start() -> int:
    """Entry point for mitmproxy."""
    parser = ArgumentParser(path.basename(__file__), description="mitmproxy request/response mutation")
    parser.add_argument('--mode', '-m', help="Start the proxy in the following mode.",
                        choices=list(Mode), default=Mode.Passive)

    args = parser.parse_args()
    proxy = Proxy(args.mode)
    return proxy.run()


class Proxy:
    """Mutate HTTP requests and responses based on the proxy mode."""
    def __init__(self, mode: Mode) -> None:
        self.set_mode(mode)

    def set_mode(self, mode: Mode) -> None:
        self.mode = mode

    def run(self) -> int:
        return 0

    def response(self, flow: Flow) -> None:
        """Proxy response handler."""
        flow.response.headers['x-tuf-mitm-proxy'] = 'true'
