# FIXME(PRO-4197): temporary bootstrap script for mitmdump
from mitmproxy.http import HTTPFlow

from .datatypes import Metadata


def response(flow: HTTPFlow) -> None:
    meta = Metadata.from_flow(flow)
    print(meta)
    pass
