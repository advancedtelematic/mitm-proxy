import json

from errors import MissingFieldError
from typing import Any, Dict, Union
from typing_extensions import Protocol


# Any readable type.
Readable = Union[str, bytes, bytearray]


# Basic JSON type as recursive types are not yet supported."""
Json = Dict[str, Any]

class Contains(Json):
    """Verify that each field exists in the object."""
    def __call__(self, *fields: str) -> None:
        for field in fields:
            if field not in self:
                raise MissingFieldError(repr(self), field)


class Encodable(Protocol):
    def _encode(self) -> Json:
        pass

class Encoder(json.JSONEncoder):
    def default(self, obj: Encodable) -> Json:
        return obj._encode()


def canonical(obj: Json) -> str:
    """Canonicalize the JSON output"""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), cls=Encoder)
