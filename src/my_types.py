from errors import ProxyError
from typing import Any, Dict, Type, Union


# Any ProxyError.
Error = Type[ProxyError]

# Any readable type.
Readable = Union[str, bytes, bytearray]

# A parsed JSON object.
Json = Dict[str, Any]
