from argparse import Namespace
from mypy_extensions import TypedDict


class Config(object):
    """Project configuration options."""
    app: 'AppConfig'
    api: 'ApiConfig'

    def __init__(self, args: Namespace) -> None:
        """Convert the command line arguments to a new instance."""
        self.app = {
            "debug": args["debug"],
        }

        self.api = {
            "host": args["host"],
            "port": args["port"],
        }


class AppConfig(TypedDict):
    debug: bool

class ApiConfig(TypedDict):
    host: str
    port: int
