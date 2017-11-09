from mitmproxy import ctx
from mitmproxy.http import HTTPFlow

from api.datatypes.metadata import Metadata


def response(flow: HTTPFlow) -> None:
    """Replace a random response signature."""

    if flow.response.headers.get('Content-Type') != "application/json":
        ctx.log.debug("skipping non-json response")
        return
    elif flow.response.text == "{}":
        ctx.log.debug("skipping empty body")
        return

    try:
        meta = Metadata.from_flow(flow)
    except Exception as e:
        ctx.log.error(f"Couldn't parse flow: {e}")
        ctx.log.debug(e.__traceback__)
        return

    try:
        ctx.log.info(f"Replacing a response signature...")
        flow.response.headers['x-tuf-mitm'] = 'true'
        old_sig = meta.signatures.random()
        new_sig = old_sig.randomize_sig()
        meta.signatures = meta.signatures.replace_key(old_sig.keyid, new_sig)
        flow.response.content = meta.to_json().encode("UTF-8")
    except Exception as e:
        ctx.log.error(f"Couldn't modify flow: {e}")
        ctx.log.debug(e.__traceback__)
