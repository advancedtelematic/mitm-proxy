from mitmproxy import ctx
from mitmproxy.http import HTTPFlow

from api.utils import is_metadata


def response(flow: HTTPFlow) -> None:
    if is_metadata(flow):
        ctx.log.debug("skipping metadata response...")
    else:
        ctx.log.debug("skipping non-metadata response...")
