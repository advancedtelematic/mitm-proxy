import logging as log

from mypy_extensions import TypedDict
from pathlib import Path
from typing import Any, Dict, Optional

from .errors import InvalidFlowPath


class Config(object):
    """Project configuration options."""
    http: 'HttpConfig'
    flow: 'FlowConfig'
    mitm: 'MitmConfig'

    def __init__(self, args: Dict[str, Any]) -> None:
        """Parses the command line arguments into a new instance."""
        log.debug(f"config args: {args}")

        self.http = {
            "host": args["http.host"],
            "port": int(args["http.port"]),
        }

        root = Path(args["flow.root"])
        if not root.exists():
            raise InvalidFlowPath(root)
        self.flow = {
            "root": root,
            "initial": args.get("flow.initial")
        }

        self.mitm = {
            "cadir": args["mitm.cadir"],
            "client_certs": args["mitm.client_certs"],
            "upstream_trusted_ca": args["mitm.upstream_trusted_ca"],
        }

class HttpConfig(TypedDict):
    """HTTP API options."""
    host: str
    port: int

class FlowConfig(TypedDict):
    """Options for starting mitmproxy flows."""
    root: Path
    initial: Optional[str]

class MitmConfig(TypedDict):
    """Startup flags for mitmproxy."""
    cadir: str
    upstream_trusted_ca: str
    client_certs: str
