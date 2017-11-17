from mitmproxy import ctx
from mitmproxy.http import HTTPFlow

from api.datatypes.metadata import Metadata
from api.datatypes.signing import Rsa
from api.utils import is_metadata


PUB_KEY = "/unsafe_keys/rsa_4096.pub"
PRIV_KEY = "/unsafe_keys/rsa_4096.key"

def response(flow: HTTPFlow) -> None:
    if is_metadata(flow):
        ctx.log.info(f"Replacing a signature with one from another key...")
    else:
        ctx.log.debug("skipping non-metadata response...")
        return

    try:
        meta = Metadata.from_flow(flow)
        rsa = Rsa.from_files(PUB_KEY, PRIV_KEY)

        sigs = meta.signatures
        old_sig = sigs.random()
        ctx.log.debug(f"deleting sig with keyid: {old_sig.keyid}")
        new_sig = rsa.sign(meta.canonical_signed().encode("UTF-8"))
        ctx.log.debug(f"adding sig with keyid: {new_sig.keyid}")
        meta.signatures = sigs.replace_key(old_sig.keyid, new_sig)

        flow.response.headers["x-mitm-flow"] = "new_signature"
        flow.response.content = meta.to_json().encode("UTF-8")
    except Exception as e:
        ctx.log.error(f"Processing error: {e}")
        ctx.log.debug(e.__traceback__)
