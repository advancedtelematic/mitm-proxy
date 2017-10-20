from typing import Any, Dict, Optional

from ..utils import contains


class Target(object):
    """An installation target."""
    filepath: str
    length: int
    hashes: Dict[str, Any]
    custom: Optional[Dict[str, Any]]
    extra: Dict[str, Any]

    def __init__(self, filepath: str, meta: Dict[str, Any]) -> None:
        contains(meta, "length", "hashes")
        self.filepath = filepath
        self.length = meta.pop("length")
        self.hashes = meta.pop("hashes")
        self.custom = meta.pop("custom", None)
        self.extra = meta

    def _encode(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"length": self.length, "hashes": self.hashes}
        if self.custom:
            out["custom"] = self.custom
        out.update(self.extra)
        return out
