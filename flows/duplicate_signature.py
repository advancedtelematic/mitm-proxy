from mitmproxy import ctx
from mitmproxy.http import HTTPFlow

from api.datatypes.metadata import Metadata
from api.utils import is_metadata


def response(flow: HTTPFlow) -> None:
    if is_metadata(flow):
        ctx.log.info(f"Duplicating a signature...")
    else:
        ctx.log.debug("skipping non-metadata response...")
        return

    try:
        meta = Metadata.from_flow(flow)
        dup_sig = meta.signatures.random()
        ctx.log.debug(f"duplicating sig with keyid: {dup_sig.keyid}")
        meta.signatures = meta.signatures.duplicate_key(dup_sig.keyid)

        flow.response.headers["x-mitm-flow"] = "duplicate_signature"
        flow.response.content = meta.to_json().encode("UTF-8")
    except Exception as e:
        ctx.log.error(f"Processing error: {e}")
        ctx.log.debug(e.__traceback__)
