import json

from logging import Formatter, LogRecord
from typing import Any, Dict, List, Union
from typing_extensions import Protocol

from .errors import MissingFieldError


# Any readable type.
Readable = Union[str, bytes, bytearray]

# An encoded type for formatting.
Encoded = Union[Dict[str, Any], List[Dict[str, Any]]]

class Encodable(Protocol):
    def _encode(self) -> Encoded:
        pass

class Encoder(json.JSONEncoder):
    def default(self, meta: Encodable) -> Encoded:
        return meta._encode()


def contains(meta: Dict[str, Any], *fields: str) -> None:
    """Verify that each field exists in the metadata object."""
    for field in fields:
        if field not in meta:
            raise MissingFieldError(repr(meta), field)

def canonical(encoded: Encoded) -> str:
    """Canonicalize the encoded object as a JSON string."""
    return json.dumps(encoded, sort_keys=True, separators=(',', ':'), cls=Encoder)


class JsonFormatter(Formatter):
    """Write JSON formatted log output."""
    def format(self, record: LogRecord) -> str:
        return json.dumps(record)
