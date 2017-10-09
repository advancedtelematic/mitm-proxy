from errors import ProxyError
from typing import Any, Dict, Type, Union


# Any ProxyError.
Error = Type[ProxyError]

# Any readable type.
Readable = Union[str, bytes, bytearray]

# Simple JSON object definition as recursive types are not yet supported.
Json = Dict[str, Any]
