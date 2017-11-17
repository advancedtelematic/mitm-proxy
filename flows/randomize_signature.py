from mitmproxy import ctx
from mitmproxy.http import HTTPFlow

from api.datatypes.metadata import Metadata
from api.utils import is_metadata


def response(flow: HTTPFlow) -> None:
    if is_metadata(flow):
        ctx.log.info(f"Randomizing a signature...")
    else:
        ctx.log.debug("skipping non-metadata response...")
        return

    try:
        meta = Metadata.from_flow(flow)
        old_sig = meta.signatures.random()
        new_sig = old_sig.randomize_sig()
        ctx.log.debug(f"replacing keyid {old_sig.keyid} with {new_sig}.keyid")
        meta.signatures = meta.signatures.replace_key(old_sig.keyid, new_sig)

        flow.response.headers["x-mitm-flow"] = "randomize_signature"
        flow.response.content = meta.to_json().encode("UTF-8")
    except Exception as e:
        ctx.log.error(f"Processing error: {e}")
        ctx.log.debug(e.__traceback__)
