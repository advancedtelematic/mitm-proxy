# FIXME(PRO-4197): temporary bootstrap script for mitmdump
from mitmproxy.http import HTTPFlow

from src.datatypes import Metadata


def response(flow: HTTPFlow) -> None:
    """Example flow that replaces one signature."""
    flow.response.headers['x-tuf-mitm'] = 'true'

    meta = Metadata.from_flow(flow)
    old_sig = meta.signatures.random()
    new_sig = old_sig.random_sig()
    meta.signatures = meta.signatures.replace_key(old_sig.keyid, new_sig)

    flow.response.content = meta.to_json()
