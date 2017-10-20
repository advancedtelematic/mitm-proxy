import json

from errors import MissingFieldError
from typing import Any, Dict, Union
from typing_extensions import Protocol


# Any readable type.
Readable = Union[str, bytes, bytearray]


# Basic JSON type as recursive types are not yet supported."""
Json = Dict[str, Any]

def contains(obj: Json, *fields: str) -> None:
    """Verify that each field exists in the object."""
    for field in fields:
        if field not in obj:
            raise MissingFieldError(repr(obj), field)


class Encodable(Protocol):
    def _encode(self) -> Json:
        pass

class Encoder(json.JSONEncoder):
    def default(self, obj: Encodable) -> Json:
        return obj._encode()


def canonical(obj: Json) -> str:
    """Canonicalize the JSON output"""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), cls=Encoder)
