import json
import pytest

from logging import Formatter, LogRecord
from typing import Any, Callable, Dict, Type, Union
from typing_extensions import Protocol

from .errors import Error, MissingFieldError


# Any readable type.
Readable = Union[str, bytes, bytearray]


def contains(meta: Dict[str, Any], *fields: str) -> None:
    """Verify that each field exists in the metadata object."""
    for field in fields:
        if field not in meta:
            raise MissingFieldError(repr(meta), field)

def canonical(meta: Dict[str, Any]) -> str:
    """Canonicalize the metadata object as a JSON string."""
    return json.dumps(meta, sort_keys=True, separators=(',', ':'), cls=Encoder)


class Encodable(Protocol):
    def _encode(self) -> Dict[str, Any]:
        pass

class Encoder(json.JSONEncoder):
    def default(self, meta: Encodable) -> Dict[str, Any]:
        return meta._encode()


class JsonFormatter(Formatter):
    """Write JSON formatted log output."""
    def format(self, record: LogRecord) -> str:
        return json.dumps(record)


def assert_raises(e: Type[Error], f: Callable, *args: Any) -> None:
    """Capture an expected error while testing."""
    with pytest.raises(e):
        f(*args)
