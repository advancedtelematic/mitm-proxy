import logging
import sys

from argparse import ArgumentParser, Namespace
from logging import config
from os import path
from typing import Any

from .modes import AlterSigned, available_modes


def start() -> Any:
    """Entry point for mitmproxy."""
    if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 required")

    setup_logging()
    args = parse_args()

    log = logging.getLogger(__name__)
    log.info(f"Staring proxy with mode: {args.mode}")
    return args.mode


def parse_args() -> Namespace:
    """Parse the command-line arguments."""
    parser = ArgumentParser(path.basename(__file__), description="TUF metadata MITM proxy")

    parser.add_argument('--mode', default=AlterSigned, choices=available_modes)
    parser.add_argument('--server', type=str, default='127.0.0.1:5456')

    return parser.parse_args()


def setup_logging() -> None:
    """Setup project-wide logging."""
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
