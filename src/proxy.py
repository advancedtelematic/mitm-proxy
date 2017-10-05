import logging
import proxy_mode

from argparse import ArgumentParser, Namespace
from logging import config
from os import path
from typing import Any

log = logging.getLogger(__name__)


def start() -> Any:
    """Entry point for mitmproxy."""
    setup_logging()
    args = parse_args()

    log.info(f"Staring proxy with mode: {args.mode}")
    return args.mode


def parse_args() -> Namespace:
    parser = ArgumentParser(path.basename(__file__),
                            description="MITM proxy for intercepting TUF metadata")
    parser.add_argument('--mode', '-m',
                        help="Start the proxy in the following mode.",
                        choices=list(proxy_mode.modes),
                        default=proxy_mode.AlterSigned)
    return parser.parse_args()


def setup_logging() -> None:
    config.dictConfig(dict(
        formatters={
            'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
        handlers={
            'h': {
                'class': 'logging.StreamHandler',
                'formatter': 'f',
                'level': logging.DEBUG
            }
        },
        root={
            'handlers': ['h'],
            'level': logging.DEBUG,
        },
    ))
