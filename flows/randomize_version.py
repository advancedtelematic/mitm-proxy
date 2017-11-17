import sys

from mitmproxy import ctx
from mitmproxy.http import HTTPFlow
from random import randrange

from api.datatypes.metadata import Metadata
from api.utils import is_metadata


def response(flow: HTTPFlow) -> None:
    if is_metadata(flow):
        ctx.log.info(f"Randomize the signed version...")
    else:
        ctx.log.debug("skipping non-metadata response...")
        return

    try:
        meta = Metadata.from_flow(flow)
        new_version = randrange(sys.maxsize)
        ctx.log.debug(f"replacing metadata version {meta.version} with {new_version}")
        meta.version = new_version

        flow.response.headers["x-mitm-flow"] = "randomize_version"
        flow.response.content = meta.to_json().encode("UTF-8")
    except Exception as e:
        ctx.log.error(f"Processing error: {e}")
        ctx.log.debug(e.__traceback__)
