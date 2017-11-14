import json

from json import JSONEncoder
from mitmproxy.http import HTTPFlow
from typing import Any, Dict, List, Union
from typing_extensions import Protocol

from .errors import MissingField


# Any readable type.
Readable = Union[str, bytes, bytearray]

# An encoded type for formatting.
Encoded = Union[Dict[str, Any], List[Dict[str, Any]]]

class Encodable(Protocol):
    def _encode(self) -> Encoded:
        pass

class Encoder(JSONEncoder):
    def default(self, meta: Encodable) -> Encoded:
        return meta._encode()


def contains(meta: Dict[str, Any], *fields: str) -> None:
    """Verify that each field exists in the metadata object."""
    for field in fields:
        if field not in meta:
            raise MissingField(repr(meta), field)

def canonical(encoded: Encoded) -> str:
    """Canonicalize the encoded object as a JSON string."""
    return json.dumps(encoded, sort_keys=True, separators=(',', ':'), cls=Encoder)


def is_metadata(flow: HTTPFlow) -> bool:
    """Inspect the flow to identify whether it is TUF metadata."""
    if flow.response.headers.get('Content-Type') != "application/json":
        return False
    elif flow.response.text == "{}":
        return False
    else:
        return True
