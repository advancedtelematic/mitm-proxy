from errors import MissingFieldError, ProxyError
from typing import Any, Dict, Type, Union


# Any ProxyError.
Error = Type[ProxyError]

# Any readable type.
Readable = Union[str, bytes, bytearray]


class Json(Dict[str, Any]):
    """Basic JSON object as recursive types are not yet supported."""

    def contains(self, *fields: str) -> None:
        """Verify that each field exists in the object."""
        for field in fields:
            if field not in self:
                raise MissingFieldError(repr(self), field)
